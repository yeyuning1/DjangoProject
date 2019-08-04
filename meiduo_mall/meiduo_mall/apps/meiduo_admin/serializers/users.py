import re

from django.utils import timezone
from rest_framework import serializers

from users.models import User


class AdminAuthSerializer(serializers.ModelSerializer):
    """管理员序列化器类"""
    username = serializers.CharField(label='用户名')
    token = serializers.CharField(label='JWT Token', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'token')

        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        try:
            user = User.objects.get(username=username, is_staff=True)
        except User.DoesNotExist:
            raise serializers.ValidationError('用户名或密码错误')

        else:

            if not user.check_password(password):
                raise serializers.ValidationError('用户名或密码错误')
            attrs['user'] = user

        return attrs

    def create(self, validated_data):
        # 获取登录用户
        user = validated_data['user']

        user.last_login = timezone.now()
        user.save()

        from rest_framework_jwt.settings import api_settings

        # 组织payload数据的方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 生成jwt token数据的方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 组织payload数据
        payload = jwt_payload_handler(user)
        # 生成jwt token
        token = jwt_encode_handler(payload)

        # 给user对象增加属性，保存jwt token的数据
        user.token = token

        return user


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器类"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')

        extra_kwars = {
            'username': {
                'min_length': 5,
                'max_length': '用户名最小长度为5',
                'error_messages': {
                    'min_length': '用户名最小长度为5',
                    'max_length': '用户名最大长度为20'
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '密码最小长度为8',
                    'max_length': '密码最大长度为20'
                }
            }
        }

    def validate_mobile(self, value):
        """手机号格式，手机号是否注册"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')

            # 手机号是否注册
        res = User.objects.filter(mobile=value).count()

        if res > 0:
            raise serializers.ValidationError('手机号已注册')

        return value