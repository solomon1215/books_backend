from blueprints.api.users.view import CreateUserView, MenuListView
from .users import user
from sanic import Blueprint

user_bp = Blueprint.group(user, url_prefix='/users')

user.add_route(CreateUserView.as_view(), name='users', uri='/')
user.add_route(MenuListView.as_view(), name='menus', uri='/menus')
