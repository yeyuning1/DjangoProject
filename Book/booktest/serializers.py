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

# BookInfoSerializer():
#    id = IntegerField(label='ID', read_only=True)
#    btitle = CharField(label='名称', max_length=20)
#    bpub_date = DateField(label='发布日期', required=True)
#    bread = IntegerField(label='阅读量', max_value=2147483647, min_value=0, required=True)
#    bcomment = IntegerField(label='评论量', max_value=2147483647, min_value=0, required=True)
