# -*- coding: utf-8 -*-

import asyncio
import asyncpg
import logging
from cachetools import cached, LRUCache, TTLCache

from config.settings import settings

_logger = logging.getLogger(__name__)


class Database(object):
    def __init__(self):
        self.db_user = settings.get('DB_USER')
        self.db_pass = settings.get('DB_PASS')
        self.db_name = settings.get('DB_NAME')
        self.db_host = settings.get('DB_HOST')
        self.db_port = settings.get('DB_PORT')

    def get_db_host(self):
        return self.db_host

    def get_db_user(self):
        return self.db_user

    def get_db_pass(self):
        return self.db_pass

    def get_db_name(self):
        return self.db_name

    @cached(cache=LRUCache(maxsize=1024))
    async def execute(self, sql):
        conn = await asyncpg.connect(user=self.db_user, password=self.db_pass, database=self.db_name, host=self.db_host, port=self.db_port)
        values = await conn.fetch(sql)
        await conn.close()
        return values

    @cached(cache=LRUCache(maxsize=1024))
    async def fetchrow(self, sql):
        conn = await asyncpg.connect(user=self.db_user, password=self.db_pass, database=self.db_name, host=self.db_host, port=self.db_port)
        values = await conn.fetchrow(sql)
        await conn.close()
        return values


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Database().execute('''SELECT * FROM tb_users'''))


