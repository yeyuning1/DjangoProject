from rest_framework import serializers

from booktest.models import BookInfo, HeroInfo


class HeroInfoSerializer(serializers.ModelField):
    class Meta:
        model = HeroInfo
        exclude = ('is_delete',)


class BookInfoSerializer(serializers.ModelSerializer):
    """图书序列化器类"""

    class Meta:
        model = BookInfo
        exclude = ('is_delete',)
        extra_kwargs = {
            'bread': {'min_value': 0, 'required': True},
            'bcomment': {'min_value': 0, 'required': False},
            'bpub_date': {'required': True}
        }
