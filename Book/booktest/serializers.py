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
