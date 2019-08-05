from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class OrderListSerializer(serializers.ModelSerializer):
    """订单序列化器类"""
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'create_time')


class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image')


class OrderSKUSerializer(serializers.ModelSerializer):
    sku = SKUSimpleSerializer(label='SKU商品')

    class Meta:
        model = OrderGoods
        fields = ('id', 'count', 'price', 'sku')


class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(label='下单用户')
    skus = OrderSKUSerializer(label='订单商品', many=True)

    create_time = serializers.DateTimeField(label='下单时间', format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = OrderInfo
        exclude = ('update_time', 'address')


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'status')
        read_only_fields = ('order_id',)
