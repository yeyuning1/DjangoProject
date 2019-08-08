from rest_framework import serializers

from goods.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        exclude = ('create_time', 'update_time')
