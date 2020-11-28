from kirin.models.auth import Users
from sanic.response import json
from sanic.views import HTTPMethodView


class CreateUserView(HTTPMethodView):

    async def post(self, request):
        result = await Users().do_signup(dict(request.json))
        return json(result)
