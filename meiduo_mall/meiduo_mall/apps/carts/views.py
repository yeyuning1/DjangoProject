from django.shortcuts import render
from django.views import View
import json
from meiduo_mall.utils import meiduo_json
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from django import http
from . import constants
from django_redis import get_redis_connection


class CartView(View):
    def post(self, request):
        # 接收，post方式，没有表单
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')

        # 验证
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        # sku_id有效
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        # 数量
        count = int(count)
        if count > 5:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '购买数量不能超过5个'})
        elif count < 1:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '购买数量不能少于1个'})
        elif count > sku.stock:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品库存不足'})

        # 处理、响应
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        if request.user.is_authenticated:
            # 登录状态，将购物车存入redis
            redis_cli = get_redis_connection('cart')
            # 向hash中存商品编号、数量
            redis_cli.hset('cart%d' % request.user.id, sku_id, count)
            # 向set中存商品编号，表示选中此商品
            redis_cli.sadd('selected%d' % request.user.id, sku_id)
        else:
            # 未登录，存入cookie
            # 1.读取cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                # 如果购物车数据已经存在，则转字典
                cart_dict = meiduo_json.loads(cart_str)
            else:
                # 如果第一次加入购物车数据，则新建字典
                cart_dict = {}

            # 2.向字典中添加或修改数据
            # cart_dict = {
            #     sku_id: {
            #         'count': count,
            #         'selected': True
            #     }
            # }
            cart_dict[sku_id] = {
                'count': count,
                'selected': True
            }

            # 3.写cookie
            cart_str = meiduo_json.dumps(cart_dict)
            # cart_str = json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response

    def get(self, request):
        # 读取购物车中的数据
        if request.user.is_authenticated:
            # 已登录，从redis中读取
            redis_cli = get_redis_connection('cart')
            # hash,包括商品编号、数量
            cart_dict_bytes = redis_cli.hgetall('cart%d' % request.user.id)
            cart_dict_int = {int(sku_id): int(count) for sku_id, count in cart_dict_bytes.items()}
            # cart_dict_int2={}
            # for key,value in cart_dict_bytes.item():
            #     cart_dict_int2[int(key)]=int(value)
            # set，商品编号，表示选中的商品
            selected_bytes = redis_cli.smembers('selected%d' % request.user.id)
            selected_int = [int(sku_id) for sku_id in selected_bytes]
            # print(cart_dict_bytes)
        else:
            # 未登录，从cookie中读取{sku_id:{selected:***,count:***}}
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = meiduo_json.loads(cart_str)
            else:
                cart_dict = {}
            # 转换字典的结构
            '''
            cookie中数据的结构
            {
                sku_id:
                {
                    count:***,
                    selected:***
                }
            }
            转换成如下结构，则与redis的后续代码一致
            {sku_id:count,..}
            [sku_id,...]
            '''
            cart_dict_int = {}
            selected_int = []
            # 遍历字典value===>{count:***,selected:***}
            for sku_id, value in cart_dict.items():
                # 将商品编号、数量存入字典中
                cart_dict_int[sku_id] = value['count']
                # 将商品选中状态存入列表中
                if value['selected']:
                    selected_int.append(sku_id)

        # 查询商品对象，构造页面中需要的数据[1,2,3]
        skus = SKU.objects.filter(pk__in=cart_dict_int.keys())
        cart_skus = []
        # 遍历商品对象
        for sku in skus:
            # 构造前端需要的结构
            cart_skus.append({
                'id': sku.id,
                'selected': str(sku.id in selected_int),
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': str(sku.price),
                'count': cart_dict_int.get(sku.id),
                'total_amount': str(cart_dict_int.get(sku.id) * sku.price)
            })

        context = {
            'cart_skus': cart_skus
        }
        return render(request, 'cart.html', context)

    def put(self, request):
        # 修改
        # 接收、验证
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected')

        # 验证
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        # sku_id有效
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})
        # 数量
        count = int(count)
        if count > 5:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '购买数量不能超过5个'})
        elif count < 1:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '购买数量不能少于1个'})
        elif count > sku.stock:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品库存不足'})
        # 选中状态
        # if selected == 'true':
        #     selected = True
        # else:
        #     selected = False

        # 处理、响应
        response = http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'cart_sku': {
                'id': sku.id,
                'selected': str(selected),
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': str(sku.price),
                'count': count,
                'total_amount': str(count * sku.price)
            }
        })

        if request.user.is_authenticated:
            # 登录状态，将购物车存入redis
            redis_cli = get_redis_connection('cart')
            # 向hash中存商品编号、数量
            redis_cli.hset('cart%d' % request.user.id, sku_id, count)
            # 向set中存商品编号，表示选中此商品
            if selected:
                redis_cli.sadd('selected%d' % request.user.id, sku_id)
            else:
                redis_cli.srem('selected%d' % request.user.id, sku_id)
        else:
            # 未登录，存入cookie
            # 1.读取cookie中的购物车数据
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                # 如果购物车数据已经存在，则转字典
                cart_dict = meiduo_json.loads(cart_str)
            else:
                # 如果第一次加入购物车数据，则新建字典
                cart_dict = {}

            # 2.向字典中添加或修改数据
            # cart_dict = {
            #     sku_id: {
            #         'count': count,
            #         'selected': True
            #     }
            # }
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 3.写cookie
            cart_str = meiduo_json.dumps(cart_dict)
            # cart_str = json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response

    def delete(self, request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 验证
        if not all([sku_id]):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数不完整'})
        # sku_id有效
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '商品编号无效'})

        response = http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })

        if request.user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            redis_cli.hdel('cart%d' % request.user.id, sku_id)
            redis_cli.srem('selected%d' % request.user.id, sku_id)
        else:
            # 读cookie
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = meiduo_json.loads(cart_str)
            else:
                cart_dict = {}
            # 改写字典
            if sku_id in cart_dict:
                del cart_dict[sku_id]
            # 写cookie
            cart_str = meiduo_json.dumps(cart_dict)
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        return response


class CartSelectionView(View):
    def put(self, request):
        # 全选、全不选
        # 接收
        dict1 = json.loads(request.body.decode())
        selected = dict1.get('selected', True)

        # 验证
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数类型错误'})
        # selected=bool(selected)

        # 处理
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        if request.user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            # 从hash中获取所有商品编号
            sku_ids = redis_cli.hkeys('cart%d' % request.user.id)
            if selected:
                # 如果选中则加入set,*表示解包[1,2,3]===>1,2,3
                redis_cli.sadd('selected%d' % request.user.id, *sku_ids)
            else:
                # 如果不选中则删除set
                redis_cli.srem('selected%d' % request.user.id, *sku_ids)
        else:
            # 读取
            cart_str = request.COOKIES.get('cart')
            # 解密
            if cart_str:
                cart_dict = meiduo_json.loads(cart_str)
            else:
                cart_dict = {}
            # 修改{sku_id:{}}
            for sku_id in cart_dict:
                # {count:***,selected:***}
                # sku_dict=cart_dict[sku_id]
                # sku_dict['selected']=selected
                cart_dict[sku_id]['selected'] = selected
            # 加密
            cart_str = meiduo_json.dumps(cart_dict)
            # 写
            response.set_cookie('cart', cart_str, max_age=constants.CART_COOKIE_EXPIRES)

        # 响应
        return response


class CartSimpleView(View):
    def get(self, request):
        # 从购物车中读取数据
        if request.user.is_authenticated:
            redis_cli = get_redis_connection('cart')
            sku_cart_bytes = redis_cli.hgetall('cart%d' % request.user.id)
            sku_cart_int = {int(sku_id): int(count) for sku_id, count in sku_cart_bytes.items()}
        else:
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                cart_dict = meiduo_json.loads(cart_str)
            else:
                cart_dict = {}
            sku_cart_int = {}
            for sku_id, dict1 in cart_dict.items():
                sku_cart_int[sku_id] = dict1.get('count')
        # 查询商品对象
        skus = SKU.objects.filter(pk__in=sku_cart_int.keys())
        # 遍历，构造前端需要的数据结构
        sku_list = []
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'count': sku_cart_int.get(sku.id),
                'default_image_url': sku.default_image.url
            })
        # 响应
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': "OK",
            'cart_skus': sku_list
        })
