from rest_framework import serializers

from goods.models import GoodsChannel


class ChannelSerializer(serializers.ModelSerializer):
    """频道序列化器类"""
    # 关联对象嵌套序列化
    category = serializers.StringRelatedField(label='一级分类名称')
    group = serializers.StringRelatedField(label='频道组名称')

    category_id = serializers.IntegerField(label='一级分类ID')
    group_id = serializers.IntegerField(label='频道组ID')

    class Meta:
        model = GoodsChannel
        exclude = ('create_time', 'update_time')
