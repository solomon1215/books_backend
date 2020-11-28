import logging

from sanic_jwt import protected
from kirin.tools.get_queryset import get_query_response, post_create_response, \
    get_instance_response, put_update_response, delete_unlink_response
from kirin.tools.table_files_dict import t_files
from sanic.response import json, text, redirect
from sanic.views import HTTPMethodView
from sanic_openapi import doc

_logger = logging.getLogger(__name__)


class LogisticsView(HTTPMethodView):
    # decorators = [protected()]  # 启用路由保护

    @doc.summary("物流跟踪")
    async def get(self, request):
        status, response = await get_query_response(request=request, table='sale_order_logistic', int_params=[],
                                                    mis_params=['code'])
        return json(response, status=status)


class OrderView(HTTPMethodView):
    # decorators = [protected()]  # 启用路由保护

    @doc.summary("订单列表")
    async def get(self, request):
        status, response = await get_query_response(request=request, table='tb_sale_order', int_params=[],
                                                    numeric_params=['purchase_price', 'price'],
                                                    mis_params=['order_id', 'customer_phone'],
                                                    sql_where='WHERE is_delete=False')
        return json(response, status=status)

    @doc.summary("订单添加")
    async def post(self, request):
        status, response = await post_create_response(request=request, table='tb_sale_order',
                                                      numeric_params=['purchase_price', 'price'],
                                                      fields=t_files.get('sale_orders_required'))
        return json(response, status=status)

    @doc.summary("订单批量删除")
    async def delete(self, request):
        status, response = await delete_unlink_response(request=request, table='tb_sale_order', fields=['is_delete'])
        return json(response, status=status)


class OrderUpdateView(HTTPMethodView):
    # decorators = [protected()]  # 启用路由保护
    @doc.summary("订单指定查询")
    async def get(self, request, order_id):
        status, response = await get_instance_response(request=request, table='tb_sale_order', id=order_id,
                                                       numeric_params=['purchase_price', 'price'])

        return json(response, status=status)

    @doc.summary("订单指定修改")
    async def put(self, request, order_id):
        status, response = await put_update_response(request=request, table='tb_sale_order', id=order_id,
                                                     numeric_params=['purchase_price', 'price'],
                                                     fields=t_files.get('sale_orders_required'))
        return json(response, status=status)
