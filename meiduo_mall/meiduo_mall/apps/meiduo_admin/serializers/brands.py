from rest_framework import serializers

from goods.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ('create_time', 'update_time')

    def validate_name(self, value):
        brand = Brand.object.get(name=value)
        if brand:
            raise serializers.ValidationError('改品牌已存在')
