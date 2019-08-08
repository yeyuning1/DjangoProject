# GET /meiduo_admin/goods/channels/?page=<页码>&page_size=<页容量>
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from meiduo_admin.serializers.channels import ChannelSerializer, ChannelGroupSerializer, ChannelCategorySerializer


class ChannelViewSet(ModelViewSet):
    """频道管理视图集"""
    lookup_value_regex = '\d+'
    permission_classes = [IsAdminUser]
    # 指定视图所使用的查询集
    queryset = GoodsChannel.objects.all()

    # 指定序列化器类
    serializer_class = ChannelSerializer


class ChannelTypesView(ListAPIView):
    """频道组视图"""
    permission_classes = [IsAdminUser]
    queryset = GoodsChannelGroup.objects.all()

    serializer_class = ChannelGroupSerializer
    pagination_class = None


class ChannelCategoriesView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = GoodsCategory.objects.filter(parent=None)

    serializer_class = ChannelCategorySerializer

    pagination_class = None
