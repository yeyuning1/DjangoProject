from rest_framework import serializers

from goods.models import SPU, SPUSpecification, SpecificationOption


class SPUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ('id', 'name')


class SpecOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项序列化器类"""

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class SPUSpecSerializer(serializers.ModelSerializer):
    """SPU规格序列化器类"""
    # 关联对象的嵌套序列化
    options = SpecOptionSerializer(label='Opt选项', many=True)

    class Meta:
        model = SPUSpecification
        fields = ('id', 'name', 'options')


class SPUSerializer(serializers.Serializer):
    """SPU序列化器类"""

    class Meta:
        model = SPU
        fields = (
            'id', 'name', 'brand', 'brand_id',
            'category1_id', 'category2_id', 'category3_id',
            'sales', 'comments'
        )
        extra_kwargs = {

        }
# TODO:1
