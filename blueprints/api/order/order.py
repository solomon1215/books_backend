import copy

from sanic import Blueprint, exceptions
from sanic.response import json, text, redirect
from sanic_openapi import doc

order = Blueprint('订单接口')


# @order.route('/')
# @doc.summary("订单接口")
# async def index(request):
#     return json({})



