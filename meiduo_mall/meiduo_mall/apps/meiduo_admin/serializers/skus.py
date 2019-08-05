from rest_framework import serializers

from goods.models import SKUImage, SKU


class SKUImageSerializer(serializers.ModelSerializer):
    sku = serializers.StringRelatedField(label='SKU商品名称')
    sku_id = serializers.IntegerField(label='SKU商品ID')

    class Meta:
        model = SKUImage
        exclude = ('create_time', 'update_time')

    def validate_sku_id(self, value):

        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku_id有误')
        return value

    def create(self, validated_data):
        sku_image = super().create(validated_data)
        sku = SKU.objects.get(id=validated_data['sku_id'])
        if not sku.default_image:
            sku.default_image = sku_image
            sku.save()
        return sku_image


class SKUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name')
