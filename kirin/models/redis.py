# -*- coding: utf-8 -*-

import asyncio
import aioredis
import redis
from cachetools import cached, LRUCache, TTLCache

from config.settings import settings


class Redis(object):
    def __init__(self, db=None):
        self.host = settings.get('REDIS_HOST')
        # self.password = settings.get('REDIS_PASS')
        self.db = db or settings.get('REDIS_DB') or 9

    async def return_result(self, result):
        return result

    @cached(cache=LRUCache(maxsize=2048))
    async def execute(self, *args, **kwargs):
        """
        执行REDIS命令
        :param args: REDIS命令参数
        :param kwargs:
        :return:
        """
        conn = await aioredis.create_connection('redis://%s/%s' % (self.host, self.db))
        result = await conn.execute(*args)
        conn.close()
        await conn.wait_closed()

        t = await self.return_result(result)
        return t

    @cached(cache=LRUCache(maxsize=2048))
    def client(self):
        """
        执行REDIS命令
        :param args: REDIS命令参数
        :param kwargs:
        :return:
        """
        conn = redis.Redis(host=self.host, password=self.password, db=self.db)
        return conn

    @cached(cache=LRUCache(maxsize=2048))
    async def create_redis(self):
        """
        Create Redis client bound to single non-reconnecting connection. https://aioredis.readthedocs.io/en/latest/api_reference.html#commands-interface
        :return:
        """
        redis = await aioredis.create_redis('redis://default:%s@%s/%s' % (self.password, self.host, self.db))
        return redis

    @cached(cache=LRUCache(maxsize=2048))
    async def create_redis_pool(self):
        """
        Create Redis client bound to connections pool.https://aioredis.readthedocs.io/en/latest/api_reference.html#commands-interface
        :return:
        """
        redis = await aioredis.create_redis_pool('redis://default:%s@%s/%s' % (self.password, self.host, self.db))
        return redis


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Redis().execute('set', 'my-key', 'value'))
    loop.run_until_complete(Redis().execute('get', 'my-key'))


