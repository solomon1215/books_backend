import datetime
import logging
import json as j
import math
import traceback

from kirin.models.database import Database
from kirin.tools.convert import datetime_converter
from kirin.tools.exceptions import params_integer_parsing_exception
from kirin.misc.response_code import ResponseCode as CODE

_logger = logging.getLogger(__name__)


async def get_query_response(request, table, int_params=[], numeric_params=[], mis_params=[],
                             sql_select=None, sql_where=None):
    int_params_kwargs = {}
    mis_params.extend(int_params)
    int_params.extend(['page', 'size'])
    for int_item in int_params:
        if int_item in ['page']:
            int_params_kwargs[int_item] = request.args and request.args.get(int_item) or 1
        elif int_item in ['size']:
            int_params_kwargs[int_item] = request.args and request.args.get(int_item) or 20
        else:
            int_params_kwargs[int_item] = request.args and request.args.get(int_item)

    parsed, status, response = params_integer_parsing_exception(**int_params_kwargs)
    if not parsed:
        return status, response

    sql_select = sql_select if sql_select else """SELECT * """
    sql_from = "FROM {}".format(table)
    sql_where = sql_where if sql_where else "WHERE is_delete=False"
    sql_order_by = "order by write_date desc"
    sql_count = "SELECT COUNT(*)"

    request.args.update(response)

    page = request.args and request.args.get('page') or 1
    size = request.args and request.args.get('size') or 20

    for key, item in request.args.items():
        if key in mis_params and key not in ['page', 'size']:
            sql_where += f"WHERE {key}='{item[0]}' " if not sql_where else f"AND {key}='{item[0]}' "
    sql_count = f"{sql_count} {sql_from} {sql_where}"
    records = await Database().fetchrow(sql_count)
    total = records[0]
    sql_query = f"{sql_select} {sql_from} {sql_where} {sql_order_by} LIMIT {size} OFFSET {size * (page - 1)}"
    records = await Database().execute(sql_query)
    data = []
    response = {}
    for r in records:
        d = dict(r)
        for numeric_param in numeric_params:
            d[numeric_param] = float(d.get(numeric_param))
        d = j.dumps(d, default=datetime_converter)
        d = j.loads(d)
        data.append(d)

    response.update({
        'total_pages': math.ceil((total * 1.0) / size),
        'current_page': page,
        'total_count': total,
        'size': size,
        'data': data
    })

    response.update(CODE.CODE_200)
    return 200, response


async def put_update_response(request, table, id, fields, numeric_params=[]):
    """
    fields: 更新字段
    """

    value = request.json
    if not value:
        response = {
            'content': '未提供数据更新值!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    sql_update = f"""UPDATE {table} """
    sql_set = """SET """
    sql_where = f"""WHERE id='{id}' """
    val_list = []
    now_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    for key, item in request.json.items():
        if key in fields:
            val_list.append(f"{key}='{item}' ")
    val_list.append(f"write_date='{now_date}' ")
    if not val_list:
        response = {
            'content': '未提供可更新数字段值!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    sql_val = ", ".join(val_list)

    sql_update = f"{sql_update} {sql_set} {sql_val} {sql_where} RETURNING *"

    try:
        records = await Database().execute(sql_update)
    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '数据更新失败!!'
        }
        response.update(CODE.CODE_406)
        return False, 406, response

    data = dict(records[0])
    for numeric_param in numeric_params:
        data[numeric_param] = float(data.get(numeric_param))
    data = j.dumps(data, default=datetime_converter)
    data = j.loads(data)
    response = {
        'content': '数据更新成功!!',
        'data': data
    }
    response.update(CODE.CODE_200)
    return 200, response


async def post_upsert_response(request, table, fields):
    """
    fields: 必输字段; body = {"company_uuid": "xxxxxxx", "user_uuid": "xxxxxxx", "data": [{},{}]}
    基于uuid字段判断是更新还是创建，uuid字段必须不为空，且设置了constrain index
    """
    company_uuid = request.args and request.args.get('company_uuid')
    if not company_uuid:
        response = {
            'content': '未提供Company UUID 参数!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    if not fields:
        response = {
            'content': '未提供必输字段!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    fields.extend(['uuid'])

    data = request.json.get('data')
    if not data:
        response = {
            'content': '未提供数据更新值!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    sql_insert = f"""INSERT INTO {table} """

    key_list = []
    val_list = []
    set_list = []

    for item in data:
        if item.keys() not in key_list:
            key_list.append(item.keys())
            if len(key_list) > 1:
                response = {
                    'content': '数据不一致!! %s' % item
                }
                response.update(CODE.CODE_406)
                return 406, response

        val = []
        for key, value in item.items():
            val.append(value)
        val_list.append(tuple(val))

    for field in fields:
        if field not in item.keys():
            response = {
                'content': '未提供必输字段! %s' % field
            }
            response.update(CODE.CODE_406)
            return False, 406, response

    for key in item.keys():
        set_str = f"{key}=excluded.{key}"
        set_list.append(set_str)

    sql_field = f"""{tuple(item.keys())}""".replace("'", "")

    if len(val_list) > 1:
        sql_val = ", ".join(val_list)
    else:
        sql_val = f"""{tuple(val_list[0])}"""

    if len(set_list) > 1:
        sql_set = ", ".join(set_list)
    else:
        sql_set = f"""{tuple(set_list[0])}"""

    sql_string = f"""{sql_insert} {sql_field} VALUES {sql_val} ON CONFLICT (uuid) DO UPDATE SET {sql_set} RETURNING id;"""

    try:
        records = await Database().execute(sql_string)
    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '数据创建失败!!'
        }
        response.update(CODE.CODE_406)
        return False, 406, response

    response = {
        'content': '数据创建成功!! %s' % records
    }
    response.update(CODE.CODE_200)
    return 200, response


async def delete_unlink_response(request, table, fields):
    """
    fields: 标记删除的字段
    """

    ids = request.args and request.args.get('ids')
    if not ids:
        response = {
            'content': '未提供ids参数!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    if not fields:
        response = {
            'content': '未提供删除标记字段!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    sql_update = f"""UPDATE {table} """
    sql_set = """SET """
    sql_where = f"WHERE id ={eval(ids)[0]}" if len(eval(ids)) == 1 else f"WHERE id in {tuple(eval(ids))} "
    val_list = []
    for field in fields:
        val_list.append(f"{field}='true' ")

    if not val_list:
        response = {
            'content': '未提供可更新数字段值!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    sql_val = ", ".join(val_list)

    sql_update = f"{sql_update} {sql_set} {sql_val} {sql_where} RETURNING id"

    try:
        await Database().execute(sql_update)
    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '数据删除失败!!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    response = {
        'content': '数据删除成功!!'
    }
    response.update(CODE.CODE_200)
    return 200, response


async def post_create_response(request, table, fields, numeric_params=[]):
    if not request.json:
        response = {
            'content': '未提供数据更新值!'
        }
        response.update(CODE.CODE_406)
        return 406, response
    if not fields:
        response = {
            'content': '未提供必输字段!'
        }
        response.update(CODE.CODE_406)
        return 406, response
    for field in fields:
        if field not in request.json.keys():
            response = {
                'content': '未提供必输字段! %s' % field
            }
            response.update(CODE.CODE_406)
            return 406, response
    now_date = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    request.json.update({'create_date': now_date, 'write_date': now_date})
    sql_insert = f"""INSERT INTO {table} """
    sql_field = f"""{tuple(request.json.keys())}""".replace("'", "")
    sql_val = f"""{tuple(request.json.values())}"""
    sql_string = f"""{sql_insert} {sql_field} VALUES {sql_val} RETURNING *;"""
    try:
        records = await Database().execute(sql_string)
    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '数据创建失败!!'
        }
        response.update(CODE.CODE_406)
        return 406, response
    data = dict(records[0])
    for numeric_param in numeric_params:
        data[numeric_param] = float(data.get(numeric_param))
    data = j.dumps(data, default=datetime_converter)
    data = j.loads(data)
    response = {
        'content': '数据创建成功!!',
        'data': data
    }
    response.update(CODE.CODE_200)
    return 200, response


async def get_instance_response(request, table, id, numeric_params=[], sql_select=None):
    sql_select = sql_select if sql_select else """SELECT * """
    sql_from = "FROM {}".format(table)
    sql_where = f"WHERE id = {id}"
    sql_string = f"""{sql_select} {sql_from} {sql_where}"""
    try:
        records = await Database().execute(sql_string)
    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '数据创建失败!!'
        }
        response.update(CODE.CODE_406)
        return 406, response

    data = dict(records[0])
    for numeric_param in numeric_params:
        data[numeric_param] = float(data.get(numeric_param))
    data = j.dumps(data, default=datetime_converter)
    data = j.loads(data)
    response = {
        'content': '数据查询成功!!',
        'data': data
    }
    response.update(CODE.CODE_200)
    return 200, response


async def delete_instance_response(request, table, id, fields):
    if not fields:
        response = {
            'content': '未提供删除标记字段!'
        }
        response.update(CODE.CODE_406)
        return 406, response
    sql_update = f"""UPDATE {table} """
    sql_set = """SET """
    sql_where = f"WHERE id ={id}"
    val_list = []
    for field in fields:
        val_list.append(f"{field}='true' ")
    sql_val = ", ".join(val_list)
    if not val_list:
        response = {
            'content': '未提供可更新数字段值!'
        }
        response.update(CODE.CODE_406)
        return 406, response
    sql_update = f"{sql_update} {sql_set} {sql_val} {sql_where} RETURNING id"
    try:
        await Database().execute(sql_update)
    except Exception as e:
        _logger.error(f"{traceback.print_exc()}")
        _logger.error(f"{e}")
        response = {
            'content': '数据删除失败!!'
        }
        return 406, response
    response = {
        'content': '数据删除成功!!'
    }
    response.update(CODE.CODE_200)

    return 200, response
