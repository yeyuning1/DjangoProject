from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.permissions import PermissionSerializer, ContentTypeSerializer, GroupSerializer, \
    PermissionSimpleSerializer, AdminSerializer, GroupSimpleSerializer
from users.models import User


class PermissionViewSet(ModelViewSet):
    """权限管理视图集"""
    permission_classes = [IsAdminUser]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    lookup_value_regex = '\d+'

    def content_types(self, request):
        types = ContentType.objects.all()
        serializer = ContentTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupViewSet(ModelViewSet):
    """用户组管理视图集"""
    permission_classes = [IsAdminUser]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    lookup_value_regex = '\d+'

    def simple(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSimpleSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminViewSet(ModelViewSet):
    """管理员管理视图集"""
    permission_classes = [IsAdminUser]
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    lookup_value_regex = '\d+'

    def simple(self, request):
        groups = Group.objects.all()
        serializer = GroupSimpleSerializer(groups, many=True)
        return Response(serializer.data)
