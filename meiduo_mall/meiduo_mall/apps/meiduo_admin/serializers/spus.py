from abc import ABC

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


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器类"""
    brand_id = serializers.IntegerField(label='品牌ID')
    brand = serializers.StringRelatedField(label='品牌名称')
    category1_id = serializers.IntegerField(label='一级分类ID')
    category2_id = serializers.IntegerField(label='二级分类ID')
    category3_id = serializers.IntegerField(label='三级分类ID')

    class Meta:
        model = SPU
        exclude = ('create_time', 'update_time')
