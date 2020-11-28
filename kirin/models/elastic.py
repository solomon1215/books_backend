# -*- coding: utf-8 -*-

import asyncio
import aioredis
from elasticsearch import Elasticsearch
from cachetools import cached, LRUCache, TTLCache

from config.settings import settings


class Elastic(object):
    def __init__(self):
        self.elastic_search_url = settings.get('ELASTIC_SEARCH_URL')
        self.elastic_search_user = settings.get('ELASTIC_SEARCH_USER')
        self.elastic_search_pass = settings.get('ELASTIC_SEARCH_PASS')

    async def return_result(self, result):
        return result

    async def search(self, *args, **kwargs):
        """
        执行Elastic命令
        :param args: Elastic命令参数
        :param kwargs:
        :return:
        """
        url = self.elastic_search_url
        es = Elasticsearch([url], http_auth=(self.elastic_search_user, self.elastic_search_pass))
        res = es.search(**kwargs)
        return res

    @cached(cache=LRUCache(maxsize=2048))
    async def count(self, *args, **kwargs):
        """
        执行Elastic命令, 返回记录数
        :param args: Elastic命令参数
        :param kwargs:
        :return:
        """
        url = self.elastic_search_url
        es = Elasticsearch([url], http_auth=(self.elastic_search_user, self.elastic_search_pass))
        res = es.count(**kwargs)
        return res


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Elastic().search(index='mdm-oe-number-d09b12c0', _source=True, body='{"query": {"match": {"id": 4282}}}'))


