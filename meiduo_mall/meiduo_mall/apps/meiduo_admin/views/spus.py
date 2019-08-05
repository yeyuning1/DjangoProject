from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser

from goods.models import SPU
from meiduo_admin.serializers.spus import SPUSimpleSerializer


class SPUSimpleView(ListAPIView):
    queryset = SPU.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = SPUSimpleSerializer
    pagination_class = None
