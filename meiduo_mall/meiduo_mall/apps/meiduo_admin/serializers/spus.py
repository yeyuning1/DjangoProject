

from rest_framework import serializers

from goods.models import SPU, SPUSpecification, SpecificationOption, GoodsCategory, Brand


class SPUSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = ('id', 'name')


class SpecOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项序列化器类"""

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class BrandsSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name')


class GoodsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')


class GoodsCategorySubsSerializer(serializers.ModelSerializer):
    subs = GoodsCategorySerializer(label='子分类', many=True)

    class Meta:
        model = GoodsCategory
        fields = ('id', 'name', 'subs')


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

    def validate(self, attrs):
        brand_id = attrs.get('brand_id')
        category1_id = attrs.get('category1_id')
        category2_id = attrs.get('category2_id')
        category3_id = attrs.get('category3_id')
        brands = Brand.objects.all()
        if brand_id not in [brand.id for brand in brands]:
            raise serializers.ValidationError('品牌有误')
        try:
            category1 = GoodsCategory.objects.get(id=category1_id)
            category2 = GoodsCategory.objects.get(id=category2_id)
        except GoodsCategory.DoesNotExist:
            raise serializers.ValidationError('一级分类有误')
        if category2_id not in [sub.id for sub in category1.subs]:
            raise serializers.ValidationError('二级分类有误')
        if category3_id not in [sub.id for sub in category2.subs]:
            raise serializers.ValidationError('三级分类有误')
        return attrs

        # 评论图片存储功能
