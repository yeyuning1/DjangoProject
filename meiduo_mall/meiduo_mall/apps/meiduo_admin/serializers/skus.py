from django.db import transaction
from rest_framework import serializers, status

from goods.models import SKUImage, SKU, SKUSpecification, SPU, SpecificationOption


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


class SKUSpecSerializer(serializers.ModelSerializer):
    """商品规格信息序列化器类"""
    spec_id = serializers.IntegerField(label='规格id')
    option_id = serializers.IntegerField(label='选项id')

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """SKU商品序列化器类"""
    # 关联对象嵌套序列化
    category = serializers.StringRelatedField(label='三级分类名称')

    spu_id = serializers.IntegerField(label='SPU编号')

    # 关联对象嵌套序列化
    specs = SKUSpecSerializer(label='商品规格信息', many=True)

    class Meta:
        model = SKU
        # 排除模型的字段
        exclude = ('create_time', 'update_time', 'default_image', 'spu', 'comments')

        extra_kwargs = {
            'sales': {
                'read_only': True
            }
        }

    def validate(self, attrs):
        # 获取spu_id
        spu_id = attrs['spu_id']
        # 检查spu商品是否存在
        try:
            spu = SPU.objects.get(id=spu_id)
        except SPU.DoesNotExist:
            raise serializers.ValidationError('spu_id不存在')
        # attrs中添加第三级分类ID
        attrs['category_id'] = spu.category3.id
        # 检查sku规格数据是否有效
        specs = attrs['specs']
        spu_specs = spu.specs.all()
        spec_count = spu_specs.count()
        # SKU商品的规格数据是否完整
        if spec_count != len(specs):
            raise serializers.ValidationError('SPU规格数据不完整')
        # SKU商品的规格数据是否一致
        specs_ids = [spec.get('spec_id') for spec in specs]
        spu_specs_ids = [spec.id for spec in spu_specs]
        # 排序
        specs_ids.sort()
        spu_specs_ids.sort()
        # 对比规格数据是否一致
        if spu_specs_ids != specs_ids:
            raise serializers.ValidationError('商品规格数据有误')

        for spec in specs:
            spec_id = spec.get('spec_id')
            option_id = spec.get('option_id')
            # 检查spec_id对应的规格是否包含option_id对应的选项
            options = SpecificationOption.objects.filter(spec_id=spec_id)
            options_ids = [option.id for option in options]

            if option_id not in options_ids:
                raise serializers.ValidationError('规格选项数据有误')

        return attrs

    def create(self, validated_data):
        specs = validated_data.pop('specs')

        with transaction.atomic():
            # 新增sku商品
            sku = SKU.objects.create(**validated_data)

            # 保存商品规格信息
            for spec in specs:
                SKUSpecification.objects.create(
                    sku=sku,
                    spec_id=spec.get('spec_id'),
                    option_id=spec.get('option_id')
                )

        return sku