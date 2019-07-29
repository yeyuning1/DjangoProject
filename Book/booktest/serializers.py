from rest_framework import serializers

from booktest.models import BookInfo


class BookInfoSerializer(serializers.ModelSerializer):
    """图书序列化器类"""

    class Meta:
        model = BookInfo
        fields = '__all__'
