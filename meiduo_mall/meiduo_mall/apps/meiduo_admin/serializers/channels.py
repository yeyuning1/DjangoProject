from rest_framework import serializers

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory


class ChannelSerializer(serializers.ModelSerializer):
    """频道序列化器类"""
    # 关联对象嵌套序列化
    category = serializers.StringRelatedField(label='一级分类名称')
    category_id = serializers.IntegerField(label='一级分类ID')

    # 关联对象嵌套序列化
    group = serializers.StringRelatedField(label='频道组名称')
    group_id = serializers.IntegerField(label='频道组ID')

    class Meta:
        model = GoodsChannel
        exclude = ('create_time', 'update_time')

    def validate_category_id(self, value):
        # 一级分类是否存在
        try:
            GoodsCategory.objects.get(id=value, parent=None)
        except GoodsCategory.DoesNotExist:
            raise serializers.ValidationError('一级分类不存在')

        return value

    def validate_group_id(self, value):
        # 频道组是否存在
        try:
            GoodsChannelGroup.objects.get(id=value)
        except GoodsChannelGroup.DoesNotExist:
            raise serializers.ValidationError('频道组不存在')

        return value


class ChannelGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsChannelGroup
        fields = ('id', 'name')


class ChannelCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')
