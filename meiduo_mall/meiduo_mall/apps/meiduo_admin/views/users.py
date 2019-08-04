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
from rest_framework.generics import CreateAPIView

from meiduo_admin.serializers.users import AdminAuthSerializer


# POST /meiduo_admin/authorizations/
from users.models import User


class AdminAuthorizeView(CreateAPIView):
    # 指定当前视图所使用的序列化器类
    serializer_class = AdminAuthSerializer
    queryset = User.objects.all()
