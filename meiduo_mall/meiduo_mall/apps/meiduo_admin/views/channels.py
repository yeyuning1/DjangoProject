# GET /meiduo_admin/goods/channels/?page=<页码>&page_size=<页容量>
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel
from meiduo_admin.serializers.channels import ChannelSerializer


class ChannelViewSet(ModelViewSet):
    """频道管理视图集"""
    permission_classes = [IsAdminUser]
    # 指定视图所使用的查询集
    queryset = GoodsChannel.objects.all()

    # 指定序列化器类
    serializer_class = ChannelSerializer
