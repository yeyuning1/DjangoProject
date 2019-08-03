from meiduo_mall.utils import meiduo_json
from django_redis import get_redis_connection


def merge_cart(request, response):
    # 这个方法使用在登录视图中，在登录时，请求报文request中不包含用户对象
    # 当状态保持后，request.user才是一个有效的用户对象
    # 从cookie中读取购物车数据
    cart_str = request.COOKIES.get('cart')
    if not cart_str:
        # cookie中没有购物车数据
        return response
    cart_dict = meiduo_json.loads(cart_str)

    # 向redis中保存购物车数据
    user = request.user
    redis_cli = get_redis_connection('cart')
    redis_pipeline = redis_cli.pipeline()
    for sku_id, sku_dict in cart_dict.items():
        # hash，存商品编号、数量
        redis_pipeline.hset('cart%d' % user.id, sku_id, sku_dict.get('count'))
        # set，表示商品选中状态
        if sku_dict.get('selected'):
            redis_pipeline.sadd('selected%d' % user.id, sku_id)
    redis_pipeline.execute()

    # 删除cookie中的购物车数据
    response.delete_cookie('cart')
    # 返回响应对象，最终返回给浏览器
    return response
