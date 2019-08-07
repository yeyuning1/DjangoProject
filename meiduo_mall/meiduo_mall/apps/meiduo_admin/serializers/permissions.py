from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from users.models import User


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器类"""

    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型序列化器类"""

    class Meta:
        model = ContentType
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化器类"""

    class Meta:
        model = Group
        fields = '__all__'


class PermissionSimpleSerializer(serializers.ModelSerializer):
    """权限简易选项展示序列化器类"""

    class Meta:
        model = Permission
        fields = ('name', 'id')


class AdminSerializer(serializers.ModelSerializer):
    """管理员用户序列化器类"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'mobile', 'password', 'user_permissions', 'groups')

        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False,
                'allow_blank': True
            }
        }

    def create(self, validated_data):
        """创建管理员用户"""
        # 设置管理员标记is_staff为True
        validated_data['is_staff'] = True

        # 创建新的管理员用户
        user = super().create(validated_data)

        # 密码加密保存
        password = validated_data['password']

        if not password:
            # 管理员默认密码
            password = '123abc'

        user.set_password(password)
        user.save()

        return user


class GroupSimpleSerializer(serializers.ModelSerializer):
    """管理员用户组简易按钮"""

    class Meta:
        model = Group
        fields = ('id', 'name')
