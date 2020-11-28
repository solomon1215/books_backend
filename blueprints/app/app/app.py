from sanic.response import json
from sanic import Blueprint, exceptions
from sanic_openapi import doc
from sanic_jwt import protected, inject_user

app = Blueprint('系统应用')


@app.route('/list')
@doc.summary("测试列表")
@protected()
@inject_user()
async def get_list(request, user):
    response = {"user": user}
    return json(response)
