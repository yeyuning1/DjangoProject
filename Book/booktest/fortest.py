import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Book.settings")
import django

django.setup()
from rest_framework import serializers


def about_django(value):
    if 'django' not in value.lower():
        raise serializers.ValidationError("图书不是关于Django的")
    return value


class User(object):
    """用户类"""

    def __init__(self, name, age):
        self.name = name
        self.age = age


class UserSerializer(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField(required=False)


class BookInfoSerializer(serializers.Serializer):
    """图书数据序列化器"""
    id = serializers.IntegerField(label='ID', read_only=True)
    btitle = serializers.CharField(label='名称', max_length=20)
    bpub_date = serializers.DateField(label='发布日期')
    bread = serializers.IntegerField(label='阅读量', required=False)
    bcomment = serializers.IntegerField(label='评论量', required=False)
    # 关联对象嵌套序列化字段
    heroinfo_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    # def validate_btitle(self, value):
    #     if 'django' not in value.lower():
    #         raise serializers.ValidationError("图书不是关于Django的")
    #     return value

    def validate(self, attrs):
        print(attrs)
        bread = attrs['bread']
        bcomment = attrs['bcomment']
        if bread < bcomment:
            raise serializers.ValidationError('阅读量小于评论量')
        return attrs


class HeroInfoSerializer(serializers.Serializer):
    """英雄数据序列化器"""
    GENDER_CHOICES = (
        (0, 'male'),
        (1, 'female')
    )
    id = serializers.IntegerField(label='ID', read_only=True)
    hname = serializers.CharField(label='名字', max_length=20)
    hgender = serializers.ChoiceField(choices=GENDER_CHOICES, label='性别', required=False)
    hcomment = serializers.CharField(label='描述信息', max_length=200, required=False)
    # hbook = serializers.PrimaryKeyRelatedField(label='图书', read_only=True)
    # hbook = serializers.PrimaryKeyRelatedField(label='图书', queryset=BookInfo.objects.all())
    # hbook = serializers.StringRelatedField(label='图书')
    # hbook = BookInfoSerializer()


if __name__ == '__main__':
    user = User('yeyuning', 18)
    serializer = UserSerializer(instance=user)
    print(serializer.data)
    u1 = {'name': 'yhx'}
    serializer = UserSerializer(data=u1)
    serializer.is_valid()
    print(serializer.errors)
    print(serializer.validated_data)
    b1 = {'btitle': 'python', 'bpub_date': '1999-01-01', 'bread': 1, 'bcomment': 2}
    serializer = BookInfoSerializer(data=b1)
    serializer.is_valid()
    print(serializer.errors)
    print(serializer.validated_data)
