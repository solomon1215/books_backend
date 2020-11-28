from .order import order_bp
from .users import user_bp
from sanic import Blueprint

api = Blueprint.group(user_bp, order_bp, url_prefix='/api/admin')
