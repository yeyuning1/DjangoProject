from rest_framework import serializers

from goods.models import SPUSpecification, SPU


class SpecsSimpleSerializer(serializers.ModelSerializer):
    # spec = serializers.StringRelatedField(label='规格名称')

    class Meta:
        model = SPUSpecification
        fields = ('id', 'name')


class SpecsSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField(label='SPU名称')
    spu_id = serializers.IntegerField(label='SPU ID')

    class Meta:
        model = SPUSpecification
        fields = ('id', 'name', 'spu_id', 'spu')

    def validate(self, attrs):
        spu_id = attrs.get('spu_id')
        name = attrs.get('name')
        try:
            spu = SPU.objects.get(id=spu_id)
        except SPU.DoesNotExist:
            raise serializers.ValidationError('spu_id有误')
        if name in [spec.name for spec in spu.specs.all()]:
            raise serializers.ValidationError('对应SPU规格已存在')
        return attrs
