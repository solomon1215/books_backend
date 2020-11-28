# -*- coding: utf-8 -*-

import asyncio
import asyncpg
import logging
import requests
import json
from cachetools import cached, LRUCache, TTLCache

from config.settings import settings

_logger = logging.getLogger(__name__)


class WxWork(object):
    def __init__(self, url):
        self.host = settings.get('WX_WORK_API_BASE_URL')
        self.url = f"{self.host}{url}"

    async def return_result(self, result):
        return result

    @cached(cache=LRUCache(maxsize=1024))
    async def get(self, *args, **kwargs):
        url = self.url
        payload = "{}"
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("GET", url, data=payload, headers=headers, params=kwargs)
        result = await self.return_result(response)
        return result

    @cached(cache=LRUCache(maxsize=1024))
    async def post(self, *args, **kwargs):
        url = self.url
        payload = "{}"
        headers = {
            'Content-Type': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=kwargs)
        result = await self.return_result(response)
        return result


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(WxWork("/gettoken").execute(corpid='xxxx', corpsecret='xxxx'))

