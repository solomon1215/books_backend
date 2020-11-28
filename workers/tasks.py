from __future__ import absolute_import, unicode_literals
import asyncio
from .celery import app
from kirin.models.database import Database


@app.task
def update_api_consume_line(user_uuid, url_md5, cost, timestamp):
    sql = f"INSERT INTO service_consume_line(user_uuid, url_md5, credit, timestamp) VALUES ('{user_uuid}', '{url_md5}', {cost}, {timestamp}) returning id"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Database().execute(sql=sql))
    return True

@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)