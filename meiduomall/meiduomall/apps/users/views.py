import re

from django.contrib.auth import login
from django.db import DatabaseError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .models import User


# Create your views here.


class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        '''
        处理注册页面发送的表单请求
        :param request:
        :return:
        '''
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # TODO:sms_code检验
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('用户名不规范')
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('密码格式不规范')
        if password2 != password:
            return HttpResponseForbidden('输入的两次密码不同')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('手机号码不规范')
        if allow != 'on':
            return HttpResponseForbidden('未勾选用户协议')
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败，请重新注册'})
        login(request, user)
        return redirect(reverse('contents:index'))


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
