from rest_framework import serializers

from goods.models import SpecificationOption, SPUSpecification


class OptionsSerializer(serializers.ModelSerializer):
    spec_id = serializers.IntegerField(label='规格ID')
    spec = serializers.StringRelatedField(label='规格名称')

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value', 'spec_id', 'spec')

    def validate(self, attrs):
        spec_id = attrs.get('spec_id')
        value = attrs.get('value')
        try:
            spec = SPUSpecification.objects.get(id=spec_id)
        except SPUSpecification.DoesNotExist:
            raise serializers.ValidationError('规格ID有误')

        count = spec.options.filter(value=value).count()
        if count > 0:
            raise serializers.ValidationError('%s已存在选项%s' % (spec, value))
        return attrs
