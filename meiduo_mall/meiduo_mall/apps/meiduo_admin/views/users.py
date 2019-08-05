# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
#
# from meiduo_admin.serializers.users import AdminAuthSerializer
#
#
# # POST /meiduo_admin/authorizations/
# class AdminAuthorizeView(APIView):
#     def post(self, request):
#         """
#         管理员登录:
#         1. 获取参数并进行校验
#         2. 服务器签发jwt token数据
#         3. 返回应答
#         """
#         # 1. 获取参数并进行校验
#         serializer = AdminAuthSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # 2. 服务器签发jwt token数据(create)
#         serializer.save()
#
#         # 3. 返回应答
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from meiduo_admin.serializers.users import AdminAuthSerializer, UserSerializer

# POST /meiduo_admin/authorizations/
from users.models import User


class AdminAuthorizeView(CreateAPIView):
    # 指定当前视图所使用的序列化器类
    serializer_class = AdminAuthSerializer
    queryset = User.objects.all()


# APIView版本
# class UserInfoView(APIView):
#     permission_classes = [IsAdminUser]
#
#     def get(self, request):
#         """
#         获取普通用户数据:
#         1. 获取keyword关键字
#         2. 查询普通用户数据
#         3. 将用户数据序列化并返回
#         """
#         keyword = request.query_params.get('keyword')
#
#         if keyword:
#             users = User.objects.filter(is_staff=False, uername__contains=keyword)
#         else:
#             users = User.objects.filter(is_staff=False)
#
#         serializer = UserSerializer(users, many=True)
#         return Response(serializer.data)

# GenericAPIView版本
# class UserInfoView(GenericAPIView):
#     permission_classes = [IsAdminUser]
#     serializer_class = UserSerializer
#
#     def get_queryset(self):
#         """返回视图所使用的查询集"""
#         keyword = self.request.query_params.get('keyword')
#
#         if keyword:
#             users = User.objects.filter(is_staff=False, username__contains=keyword)
#         else:
#             users = User.objects.filter(is_staff=False)
#         return users
#
#     def get(self, request):
#
#         users = self.get_queryset()
#         serializer = self.get_serializer(users, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     def post(self, request):
#         """
#         新增用户数据:
#         1. 获取参数并进行校验
#         2. 创建并保存新用户数据
#         3. 将新用户数据序列化并返回
#         """
#         # 1. 获取参数并进行校验
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # 2. 创建并保存新用户数据(create)
#         serializer.save()
#
#         # 3. 将新用户数据序列化并返回
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
class UserInfoView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        """返回视图所使用的查询集"""
        # 1. 获取keyword关键字
        keyword = self.request.query_params.get('keyword')

        # 2. 查询普通用户数据
        if keyword:
            users = User.objects.filter(is_staff=False, username__contains=keyword)
        else:
            users = User.objects.filter(is_staff=False)

        return users
