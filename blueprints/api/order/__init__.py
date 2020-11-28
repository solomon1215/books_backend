from blueprints.api.order.views import LogisticsView, OrderView, OrderUpdateView

from .order import order

from sanic import Blueprint

order_bp = Blueprint.group(order, url_prefix='/orders')

order.add_route(LogisticsView.as_view(), name='Logistics', uri='/logistics')
order.add_route(OrderView.as_view(), name='order', uri='/')
order.add_route(OrderUpdateView.as_view(), name='order', uri='/<order_id>')
