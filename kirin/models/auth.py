import hashlib
import contextlib
from sanic import exceptions
from sanic.response import json, text
from workers import tasks
from kirin.models.database import *
from passlib.context import CryptContext
from kirin.models.redis import Redis
from kirin.misc.response_code import ResponseCode as CODE

import pytz
import datetime
import time
import ipaddress
import itertools
import logging
import hmac
import uuid
from json import dumps

from collections import defaultdict
from hashlib import sha256
from itertools import chain, repeat
import passlib.context
from functools import wraps
from config.settings import settings
from kirin.tools.exceptions import AccessDenied, ValidationError, UserError, AccessError, Warning

_logger = logging.getLogger(__name__)

default_crypt_context = CryptContext(
    # kdf which can be verified by the context. The default encryption kdf is
    # the first of the list
    ['pbkdf2_sha512', 'plaintext'],
    # deprecated algorithms are still verified as usual, but ``needs_update``
    # will indicate that the stored hash should be replaced by a more recent
    # algorithm. Passlib 1.6 supports an `auto` value which deprecates any
    # algorithm but the default, but Ubuntu LTS only provides 1.5 so far.
    deprecated=['plaintext'],
)


async def extend_payload(payload, *args, **kwargs):
    return payload


async def application_auth(user_id, key, sign, timestamp):
    # if not (key and timestamp and sign):
    #     raise exceptions.abort(403, "Missing key_frm or timestamp_frm or sign_frm!")

    timestamp_frm = timestamp
    timestamp_now = time.time()

    if timestamp_now - timestamp_frm > 60 * 10:
        raise exceptions.abort(403, "Your sign is timed out!")

    secret = await Redis().execute('hget', user_id, key)
    if not secret:
        raise exceptions.abort(403, "Your sign can't be parsed!")

    sign_string = "%s,%s,%s" % (key, timestamp_frm, secret.decode())
    sign_api = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()
    if sign != sign_api:
        raise exceptions.abort(403, "Your sign can't be parsed!")

    return True


async def authenticate(request, *args, **kwargs):
    username = (request.json and request.json.get("username", None)) or (request.args and request.args.get('username'))
    password = (request.json and request.json.get("password", None)) or (request.args and request.args.get('password'))
    key = (request.json and request.json.get("key", None)) or (request.args and request.args.get('key'))
    sign = (request.json and request.json.get("sign", None)) or (request.args and request.args.get('sign'))
    timestamp = (request.json and request.json.get("timestamp", None)) or (
            request.args and request.args.get('timestamp'))

    if not (username and password):
        raise exceptions.SanicException("Missing username or password.")

    auth = await Users(username, password).authenticate()

    if not auth.get('valid'):
        raise exceptions.SanicException("Wrong username or password.")

    # 根据API访问类型判断用户是外部用户还是内部用户
    if auth.get('api_access') in ['external']:
        if not (key and sign and timestamp):
            raise exceptions.SanicException("Missing key or sign or timestamp!")

        user_id = auth.get('user_id')

        await application_auth(user_id, key, sign, timestamp)

    return auth


async def store_refresh_token(user_id, refresh_token, *args, **kwargs):
    key = 'refresh_token_{user_id}'.format(user_id=user_id)
    await Redis().execute('set', key, refresh_token)


async def retrieve_refresh_token(request, user_id, *args, **kwargs):
    key = f'refresh_token_{user_id}'
    return await Redis().execute('get', key)


async def retrieve_user(request, *args, **kwargs):
    """
    获取用户信息
    :param request:
    :param args:
    :param kwargs:
    :return:
    """

    payload = await request.app.auth.extract_payload(request)
    if not payload:
        raise exceptions.SanicException("No user_id extracted from the token.")

    user_id = payload.get('user_id')

    return payload if user_id else None


def api_trace(verify=True):
    """
    接口调用统计: API内部用户只统计接口调用次数；外部用户增加接口访问范围和计费统计...
    :param verify:
    :return:
    """

    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            result = await f(request, *args, **kwargs)
            response = {}
            payload = await request.app.auth.extract_payload(request, verify=verify)
            if not payload:
                response.update(CODE.CODE_401)
                return json(response)

            user_id = payload.get('user_id')
            if not user_id:
                response.update(CODE.CODE_401)
                return json(response)

            redis = await Redis(9).create_redis_pool()
            api_access = await redis.hget(user_id, 'api_access')

            api_url = request.path
            complete_url = "%s%s" % (settings['BASE_URL'], api_url)
            url_md5 = hashlib.md5()
            url_md5.update(complete_url.encode('utf8'))
            url_md5 = url_md5.hexdigest()

            api_url_exist = await redis.hexists(user_id, url_md5)
            if not api_url_exist and api_access in [b'external']:
                response.update(CODE.CODE_401)
                return json(response)

            balance_field = 'balance'
            balance = await redis.hget(user_id, balance_field) if api_access in [b'external'] else 0.0
            cost = await redis.hget(user_id, url_md5) if api_access in [b'external'] else 0.0
            if cost > balance and api_access in [b'external']:
                response.update(CODE.CODE_913)
                return json(response)

            # channel = settings.get('REDIS_CHANNEL')
            # if not channel:
            #     response.update(CODE.CODE_401)
            #     return json(response)
            #
            # message = {
            #     'user_id': user_id,
            #     'api_url': api_url,
            #     'credit': float(cost),
            #     'timestamp': int(time.time())
            # }

            tr = redis.multi_exec()
            tr.hincrbyfloat(user_id, balance_field, float(cost) * (-1.0))
            # tr.xadd(channel, message)
            # tr.publish(channel=channel, message=dumps(message))
            await tr.execute()
            redis.close()
            await redis.wait_closed()
            tasks.update_api_consume_line.delay(user_id, url_md5, float(cost), time.time())
            return result

        return decorated_function

    return decorator


def open_api_authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            key_frm = request.headers.get('Key')
            timestamp_frm = request.headers.get('Timestamp')
            sign_frm = request.headers.get('Sign')
            # print(sign_frm)

            if not (key_frm and timestamp_frm and sign_frm):
                raise exceptions.abort(403, "Missing key_frm or timestamp_frm or sign_frm!")

            timestamp_frm = int(timestamp_frm)
            timestamp_now = int(time.time())

            if timestamp_now - timestamp_frm > 60 * 10:
                raise exceptions.abort(403, "Your sign is timed out!")

            sql_config = "select token_key,token_secret from mdm_interface_control where token_key='%s'" % key_frm
            _logger.info(sql_config)
            configs = await Database().execute(sql_config)
            if len(configs) != 1:
                raise exceptions.abort(403, "can not find key [%s]" % key_frm)

            key_api = configs[0]["token_key"]
            secret_api = configs[0]["token_secret"]

            sign_string = "%s,%s,%s" % (key_api, timestamp_frm, secret_api['secret'])

            sign_api = hashlib.sha256(sign_string.encode('utf-8')).hexdigest()

            if sign_frm != sign_api:
                raise exceptions.abort(403, "Your sign can't be parsed!")

            response = await f(request, *args, **kwargs)
            return response

        return decorated_function

    return decorator


class Users(object):
    def __init__(self, login=None, password=None):
        ctx = self._crypt_context()
        self.login = login
        self.password = password
        # self.password = self._crypt_context().encrypt(password)

    async def return_result(self, result):
        return result

    async def authenticate(self):
        """
        用户验证: 用CryptContext方法进行验证 ODOO11的密码字段是 password_crypt；ODOO12的密码字段是 password
        :return:
        """
        valid = False
        uid = None

        sql = f"""
        SELECT COALESCE(password, '') AS password,COALESCE(id, null) AS id
        FROM tb_users WHERE login='{self.login}'"""
        values = await Database().execute(sql)
        if values:
            hashed = values[0]['password']
            valid, replacement = self._crypt_context().verify_and_update(self.password, hashed)
            if valid:
                uid = values[0]['id']
        result = {'valid': valid, 'user_id': uid, }
        print(result)
        t = await self.return_result(result)
        return t

    async def do_signup(self, values):
        """
        用户注册；传入参数VALUES必须为字典，包含name, users, password, confirm_password
        :param values:
        :return:
        """
        if not isinstance(values, dict):
            raise exceptions.abort(403, "传入参数必须为字典！")

        # name = values.get('name')
        login = values.get('login')
        password = values.get('password')
        confirm_password = values.get('confirm_password')

        if password != confirm_password:
            raise exceptions.abort(403, "Passwords do not match; please retype them.")

        sql_check_existing = f"SELECT id, login FROM tb_users WHERE login = '{login}'"

        existing = await Database().execute(sql_check_existing)
        if existing:
            raise exceptions.abort(403, "Another user is already registered using this users.")

        password = self._crypt_context().encrypt(password)

        sql_create_user = f"INSERT INTO tb_users (login, password) VALUES ('{login}','{password}');"

        user_id = await Database().execute(sql_create_user)

        result = {'valid': True, 'uid': user_id and user_id[0].get('id'), 'users': login}

        t = await self.return_result(result)
        return t

    def _crypt_context(self):
        """ Passlib CryptContext instance used to encrypt and verify
        passwords. Can be overridden if technical, legal or political matters
        require different kdfs than the provided default.
        Requires a CryptContext as deprecation and upgrade notices are used
        internally
        """
        return default_crypt_context
