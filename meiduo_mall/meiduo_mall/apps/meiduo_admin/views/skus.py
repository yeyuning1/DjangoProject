from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage
from meiduo_admin.serializers.skus import SKUImageSerializer


class SKUImageViewSet(ModelViewSet):
    serializer_class = SKUImageSerializer
    permission_classes = [IsAdminUser]
    queryset = SKUImage.objects.all()
    lookup_value_regex = '\d+'
