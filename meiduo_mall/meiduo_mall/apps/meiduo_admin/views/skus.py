from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.skus import SKUImageSerializer, SKUSimpleSerializer


class SKUImageViewSet(ModelViewSet):
    serializer_class = SKUImageSerializer
    permission_classes = [IsAdminUser]
    queryset = SKUImage.objects.all()
    lookup_value_regex = '\d+'


class SKUSimpleView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SKUSimpleSerializer
    queryset = SKU.objects.all()
    pagination_class = None
