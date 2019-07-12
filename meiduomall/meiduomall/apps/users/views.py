from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .models import User


# Create your views here.


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        # 获取数据库中该用户名对应的个数
        count = User.objects.filter(username=username).count()

        # 拼接参数, 返回:
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        print(count)
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'count': count})
