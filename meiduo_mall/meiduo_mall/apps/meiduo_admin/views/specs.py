from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification
from meiduo_admin.serializers.specs import SpecsSerializer, SpecsSimpleSerializer


class SpecsViewSet(ModelViewSet):
    lookup_value_regex = '\d+'
    permission_classes = [IsAdminUser]
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecsSerializer


class SpecsSimpleView(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecsSimpleSerializer
    pagination_class = None
