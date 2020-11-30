from kirin.models.auth import Users
from sanic.response import json
from sanic.views import HTTPMethodView
from kirin.misc.response_code import ResponseCode as CODE


class CreateUserView(HTTPMethodView):

    async def post(self, request):
        result = await Users().do_signup(dict(request.json))
        return json(result)


class MenuListView(HTTPMethodView):

    async def get(self, request):
        response = {
            'data': [{'id': 102, 'authName': '订单管理', 'children': [{'authName': '订单列表', 'path': 'orders'}]}
                     ]}
        response.update(CODE.CODE_200)
        return json(response, status=200)
