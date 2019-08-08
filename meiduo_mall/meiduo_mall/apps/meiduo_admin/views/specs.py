from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification
from meiduo_admin.serializers.specs import SpecsSerializer


class SpecsViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecsSerializer
