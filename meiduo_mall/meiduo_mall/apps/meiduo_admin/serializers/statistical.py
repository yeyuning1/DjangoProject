from rest_framework import serializers

from goods.models import GoodsVisitCount


class GoodsVisitSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(label='分类')

    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')
