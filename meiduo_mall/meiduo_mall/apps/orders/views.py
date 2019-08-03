from django.shortcuts import render
from django.views import View
from django import http
from meiduo_mall.utils.login import LoginRequiredMixin
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU
from users.models import Address
import json
from meiduo_mall.utils.response_code import RETCODE
from .models import OrderInfo, OrderGoods
from datetime import datetime
from django.db import transaction
from django.core.paginator import Paginator


class SettlementView(LoginRequiredMixin, View):
    def get(self, request):
        # 收货地址
        addresses = request.user.adresses.filter(is_delete=False)
        # addresses=Address.objects.filter(is_delete=False,user_id=request.user.id)

        # 查询购物车中选中的商品
        redis_cli = get_redis_connection('cart')
        # 从hash中读取商品编号、数量
        cart_dict_bytes = redis_cli.hgetall('cart%d' % request.user.id)
        cart_dict_int = {int(sku_id): int(count) for sku_id, count in cart_dict_bytes.items()}
        # 从set中读取选中的商品编号
        cart_selected_bytes = redis_cli.smembers('selected%d' % request.user.id)
        cart_selected_int = [int(sku_id) for sku_id in cart_selected_bytes]
        # 查询选中的商品
        skus = SKU.objects.filter(pk__in=cart_selected_int)
        # 遍历，构造html中需要的数据
        sku_list = []
        total_count = 0
        total_amount = 0
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price,
                'count': cart_dict_int.get(sku.id),
                'total_amount': sku.price * cart_dict_int.get(sku.id)
            })
            # 计算总数量
            total_count += cart_dict_int.get(sku.id)
            # 计算总金额
            total_amount += sku.price * cart_dict_int.get(sku.id)

        # 运费
        transit = 10
        # 实付款
        payment_amount = total_amount + transit

        context = {
            'addresses': addresses,
            'sku_list': sku_list,
            'total_count': total_count,
            'total_amount': total_amount,
            'transit': transit,
            'payment_amount': payment_amount
        }

        return render(request, 'place_order.html', context)


class CommitView(LoginRequiredMixin, View):
    def post(self, request):
        # 接收
        dict1 = json.loads(request.body.decode())
        address_id = dict1.get('address_id')
        pay_method = dict1.get('pay_method')

        # 验证
        if not all([address_id, pay_method]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        # 收货地址
        try:
            address = Address.objects.get(pk=address_id, is_delete=False, user_id=request.user.id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '收货地址无效'})
        # 支付方式
        if pay_method not in [1, 2]:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '支付方式无效'})

        # 处理（业务最多）
        user = request.user
        now = datetime.now()
        # 1.查询购物车选中的商品
        redis_cli = get_redis_connection('cart')
        # 从hash中读取商品编号、数量
        cart_dict_bytes = redis_cli.hgetall('cart%d' % request.user.id)
        cart_dict_int = {int(sku_id): int(count) for sku_id, count in cart_dict_bytes.items()}
        # 从set中读取选中的商品编号
        cart_selected_bytes = redis_cli.smembers('selected%d' % request.user.id)
        cart_selected_int = [int(sku_id) for sku_id in cart_selected_bytes]

        with transaction.atomic():  # 禁止自动提交
            # 开启事务
            sid = transaction.savepoint()

            # 2.创建订单基本对象
            order_id = '%s%09d' % (now.strftime('%Y%m%d%H%M%S'), user.id)
            total_count = 0
            total_amount = 0
            if pay_method == '1':
                # 待发货
                status = 1
            else:
                # 待支付
                status = 2
            order = OrderInfo.objects.create(
                order_id=order_id,
                user_id=user.id,
                address_id=address_id,
                total_count=0,
                total_amount=0,
                freight=10,
                pay_method=pay_method,
                status=status
            )

            # 3.查询商品对象
            skus = SKU.objects.filter(pk__in=cart_selected_int)

            # 4.遍历
            for sku in skus:
                cart_count = cart_dict_int.get(sku.id)
                # 4.1判断库存，不足则提示,如果足够则继续执行
                if sku.stock < cart_count:
                    # 回滚事务
                    transaction.savepoint_rollback(sid)
                    # 给出提示
                    return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品[%d]库存不足' % sku.id})

                # 强制停止
                # import time
                # time.sleep(5)

                # 4.2修改sku的库存、销量
                # sku.stock -= cart_count
                # sku.sales += cart_count
                # sku.save()

                # 4.2使用乐观锁进行修改
                stock_old = sku.stock
                stock_new = sku.stock - cart_count
                sales_new = sku.sales + cart_count
                result = SKU.objects.filter(pk=sku.id, stock=stock_old).update(stock=stock_new, sales=sales_new)
                # result表示sql语句修改数据的个数
                if result == 0:
                    # 库存发生变化，未成功购买
                    transaction.savepoint_rollback(sid)
                    return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '服务器忙，请稍候重试'})

                # 4.3创建订单商品对象
                order_sku = OrderGoods.objects.create(
                    order_id=order_id,
                    sku_id=sku.id,
                    count=cart_count,
                    price=sku.price
                )

                # 4.4 计算总金额、总数量
                total_count += cart_count
                total_amount += sku.price * cart_count

            # 5.修改订单对象的总金额、总数量
            order.total_count = total_count
            order.total_amount = total_amount + 10
            order.save()

            # 提交
            transaction.savepoint_commit(sid)

        # 6.删除购物车中选中的商品
        redis_cli.hdel('cart%d' % request.user.id, *cart_selected_int)
        redis_cli.srem('selected%d' % request.user.id, *cart_selected_int)

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})


class SuccessView(LoginRequiredMixin, View):
    def get(self, request):
        # 接收
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }

        return render(request, 'order_success.html', context)


class InfoView(LoginRequiredMixin, View):
    def get(self, request, page_num):
        # 查询当前登录用户的所有订单
        order_list = request.user.orders.order_by('-create_time')

        # 分页
        paginator = Paginator(order_list, 2)
        # 获取当前页数据
        page = paginator.page(page_num)

        # 遍历当前页数据，转换页面中需要的结构
        order_list2 = []
        for order in page:
            # 获取当前订单中所有订单商品
            detail_list = []
            for detail in order.skus.all():
                detail_list.append({
                    'default_image_url': detail.sku.default_image.url,
                    'name': detail.sku.name,
                    'price': detail.price,
                    'count': detail.count,
                    'total_amount': detail.price * detail.count
                })

            order_list2.append({
                'create_time': order.create_time,
                'order_id': order.order_id,
                'details': detail_list,
                'total_amount': order.total_amount,
                'freight': order.freight,
                'status': order.status
            })

        context = {
            'page': order_list2,
            'page_num': page_num,
            'total_page': paginator.num_pages
        }
        return render(request, 'user_center_order.html', context)


class CommentView(LoginRequiredMixin, View):
    def get(self, request):
        # 接收订单编号
        order_id = request.GET.get('order_id')

        # 查询订单商品列表
        try:
            order = OrderInfo.objects.get(pk=order_id, user_id=request.user.id)
        except:
            return http.Http404('商品编号无效')

        # 获取订单的所有商品
        skus = []
        # detail表示OrderGoods类型的对象
        for detail in order.skus.filter(is_commented=False):
            skus.append({
                'sku_id': detail.sku.id,
                'default_image_url': detail.sku.default_image.url,
                'name': detail.sku.name,
                'price': str(detail.price),
                'order_id': order_id
            })

        context = {
            'skus': skus
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        # 接收
        data = json.loads(request.body.decode())
        order_id = data.get('order_id')
        sku_id = data.get('sku_id')
        comment = data.get('comment')
        score = data.get('score')
        is_anonymous = data.get('is_anonymous')

        # 验证
        if not all([order_id, sku_id, comment, score]):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '参数不完整'
            })
        if not isinstance(is_anonymous, bool):
            return http.JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '是否匿名参数错误'
            })
        # 查询OrderGoods对象
        order_goods = OrderGoods.objects.get(order_id=order_id, sku_id=sku_id)
        order_goods.comment = comment
        order_goods.score = int(score)
        order_goods.is_anonymous = is_anonymous
        order_goods.is_commented = True
        order_goods.save()

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })


class CommentSKUView(View):
    def get(self, request, sku_id):
        # 查询指定sku_id的所有评论信息
        comments = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True)
        comment_list = []
        # detail表示OrderGoods对象
        for detail in comments:
            username = detail.order.user.username
            if detail.is_anonymous:
                username = '******'
            comment_list.append({
                'username': username,
                'comment': detail.comment,
                'score': detail.score
            })

        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': "OK",
            'goods_comment_list': comment_list
        })
