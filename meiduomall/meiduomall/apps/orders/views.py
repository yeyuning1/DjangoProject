import json
import logging
from decimal import Decimal
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection
from areas.models import Address
from goods.models import SKU
from meiduomall.utils.response_code import RETCODE
from orders.models import OrderInfo, OrderGoods
from users.utils import LoginRequiredJSONMixin

logger = logging.getLogger('django')


class OrderSettlementView(View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 获取登录用户
        user = request.user
        # 查询地址信息
        try:
            addresses = Address.objects.filter(user=request.user,
                                               is_delete=False)
        except Address.DoesNotExist:
            addresses = None

        # 从 redis 购物车中查询出被勾选的商品信息
        redis_conn = get_redis_connection('carts')
        item_dict = redis_conn.hgetall('carts_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(item_dict[sku_id])

        total_count = 0
        total_amount = Decimal(0.00)
        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.amount = sku.count * sku.price

            total_count += sku.count
            total_amount += sku.amount

        freight = Decimal('10.00')

        # 渲染界面
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 获取当前要保存的信息和订单商品信息
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return HttpResponseForbidden('参数address_id错误')

        # 判断 pay_method 是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'],
                              OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return HttpResponseForbidden('参数pay_method有误')

        # 获取登录用户
        user = request.user

        # 生成订单编号：年月日时分秒 + 用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # # 保存订单基本信息 OrderInfo
        # -----------------------------------------------------------------------------
        # order = OrderInfo.objects.create(
        #     order_id=order_id,
        #     user=user,
        #     address=address,
        #     total_count=0,
        #     total_amount=Decimal('0'),
        #     freight=Decimal('10.00'),
        #     pay_method=pay_method,
        #     status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        #     if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
        #     else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        # )
        # # 从redis 读取购物车中被勾选的商品信息
        # redis_conn = get_redis_connection('carts')
        # item_dict = redis_conn.hgetall('carts_%s' % user.id)
        # cart_selected = redis_conn.smembers('selected_%s' % user.id)
        # carts = {}
        # for sku_id in cart_selected:
        #     carts[int(sku_id)] = int(item_dict[sku_id])
        #
        # # 获取选中的商品id
        # sku_ids = carts.keys()
        #
        # # 遍历购物车中被勾选的商品信息
        # for sku_id in sku_ids:
        #     # 查询 SKU 信息
        #     sku = SKU.objects.get(id=sku_id)
        #     # 判断 SKU 库存
        #     sku_count = carts[sku.id]
        #     if sku_count > sku.stock:
        #         return JsonResponse({
        #             'code': RETCODE.OK,
        #             'errmsg': '库存不足'
        #         })
        #
        #     # SKU 减少库存，增加销量
        #     sku.stock -= sku_count
        #     sku.sales += sku_count
        #
        #     # 保存订单商品信息 OrderGoods(多)
        #     OrderGoods.objects.create(
        #         order=order,
        #         sku=sku,
        #         count=sku_count,
        #         price=sku.price,
        #     )
        #
        #     # 保存商品订单中总价和总数量
        #     order.total_count += sku_count
        #     order.total_amount += (sku_count * sku.price)
        #
        # # 添加邮费和保存订单信息
        # order.save()
        #
        # # 清除购物车中已结算的商品
        # redis_conn.hdel('carts_%s' % user.id, *cart_selected)
        # redis_conn.srem('carts_%s' % user.id, *cart_selected)
        #
        # # 响应提交订单结果
        # return JsonResponse({
        #     'code': RETCODE.OK,
        #     'errmsg': '下单成功',
        #     'order_id': order.order_id
        # })
        # -----------------------------------------------------------------------------
        # 显式的开启一个事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()

            # 暴力回滚
            try:
                # 保存订单基本信息 OrderInfo（一）
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                selected = redis_conn.smembers('selected_%s' % user.id)
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])
                sku_ids = carts.keys()

                # 遍历购物车中被勾选的商品信息
                for sku_id in sku_ids:
                    # 查询SKU信息
                    sku = SKU.objects.get(id=sku_id)
                    # 判断SKU库存
                    sku_count = carts[sku.id]
                    if sku_count > sku.stock:
                        # 出错就回滚
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({
                            'code': RETCODE.STOCKERR,
                            'errmsg': '库存不足'})

                    # SKU减少库存，增加销量
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()

                    # 修改SPU销量
                    sku.goods.sales += sku_count
                    sku.goods.save()

                    # 保存订单商品信息 OrderGoods（多）
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )

                    # 保存商品订单中总价和总数量
                    order.total_count += sku_count
                    order.total_amount += (sku_count * sku.price)

                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({
                    'code': RETCODE.DBERR,
                    'errmsg': '下单失败'})

            # 提交订单成功，显式的提交一次事务
            transaction.savepoint_commit(save_id)

        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *selected)
        pl.srem('selected_%s' % user.id, *selected)
        pl.execute()

        # 响应提交订单结果
        return JsonResponse({'code': RETCODE.OK,
                             'errmsg': '下单成功',
                             'order_id': order.order_id})
