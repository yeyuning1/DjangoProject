from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from goods.models import SpecificationOption
from meiduo_admin.serializers.options import OptionsSerializer


class OptionsViewSet(ModelViewSet):
    lookup_value_regex = '\d+'
    permission_classes = [IsAdminUser]
    serializer_class = OptionsSerializer
    queryset = SpecificationOption.objects.all()
