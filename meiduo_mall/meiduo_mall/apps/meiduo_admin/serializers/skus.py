from rest_framework import serializers

from goods.models import SKUImage


class SKUImageSerializer(serializers.ModelSerializer):
    sku = serializers.StringRelatedField(label='SKU商品名称')
    sku_id = serializers.IntegerField(label='SKU商品ID')

    class Meta:
        model = SKUImage
        exclude = ('create_time', 'update_time')
