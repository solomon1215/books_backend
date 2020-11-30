from blueprints.api.order.views import OrderView, OrderUpdateView

from .order import order

from sanic import Blueprint

order_bp = Blueprint.group(order, url_prefix='/orders')

order.add_route(OrderView.as_view(), name='order', uri='/')
order.add_route(OrderUpdateView.as_view(), name='order', uri='/<order_id>')
