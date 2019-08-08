from rest_framework.generics import ListAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPU, SPUSpecification, GoodsCategory, Brand
from meiduo_admin.serializers.spus import SPUSimpleSerializer, SPUSpecSerializer, SPUSerializer, \
    GoodsCategorySerializer, BrandsSimpleSerializer, GoodsCategorySubsSerializer


class SPUSimpleView(ListAPIView):
    """SPU简易展示视图"""
    queryset = SPU.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = SPUSimpleSerializer
    pagination_class = None


# class SPUSpecView(GenericAPIView):
#     permission_classes = [IsAdminUser]
#
#     def get(self, request, pk):
#         specs = SPUSpecification.objects.filter(spu_id=pk)
#         serializer = SPUSpecSerializer(specs, many=True)
#         return Response(serializer.data)

class SPUSpecView(ListAPIView):
    """SPU规格视图"""
    permission_classes = [IsAdminUser]
    serializer_class = SPUSpecSerializer
    pagination_class = None

    def get_queryset(self):
        pk = self.kwargs['pk']
        return SPUSpecification.objects.filter(spu_id=pk)


class BrandsSimpleView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = Brand.objects.all()
    pagination_class = None
    serializer_class = BrandsSimpleSerializer


class GoodsCategoriesView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = GoodsCategory.objects.filter(parent=None)
    serializer_class = GoodsCategorySerializer
    pagination_class = None


class GoodsCategorySubsView(RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GoodsCategorySubsSerializer
    pagination_class = None
    queryset = GoodsCategory.objects.all()


class SPUViewSet(ModelViewSet):
    """SPU管理视图集"""
    permission_classes = [IsAdminUser]
    serializer_class = SPUSerializer
    queryset = SPU.objects.all()
