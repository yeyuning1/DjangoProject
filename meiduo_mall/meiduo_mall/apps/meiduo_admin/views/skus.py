from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.skus import SKUImageSerializer, SKUSimpleSerializer, SKUSerializer


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


class SKUViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = SKUSerializer
    queryset = SKU.objects.all()
    lookup_value_regex = '\d+'

    def get_queryset(self):
        keyword = self.request.query_params['keyword']
        if keyword:
            skus = SKU.objects.filter(Q(name__contains=keyword) |
                                      Q(caption__contains=keyword))
        else:
            skus = SKU.objects.all()
        return skus
