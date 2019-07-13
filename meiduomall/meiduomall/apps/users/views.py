import re

from django.contrib.auth import login, authenticate
from django.db import DatabaseError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from .models import User


# Create your views here.
# -------------------------------------------------

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
        sms_code = request.POST.get('sms_code')
        if not all([username, password, password2, mobile, allow, sms_code]):
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
        # 检查短信验证码是否正确
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_code_%s' % mobile)
        if sms_code_server is None:
            return render(request,
                          'register.html',
                          {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_server.decode('utf-8') != sms_code:
            return render(request,
                          'register.html',
                          {'sms_code_errmsg': '输入短信验证码有误'})

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


# -------------------------------------------------
# 以下为登陆
class LoginView(View):
    '''用户登陆'''

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        '''
        验证用户登陆信息
        :param request:
        :return:
        '''
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 检查参数
        if not all([username, password, remembered]):
            return HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入正确的用户名或手机号')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('密码最少8位，最长20位')

        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        # 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            # 用户无需记住密码， 设置session的周期为0
            request.session.set_expiry(0)
        else:
            # 用户选择记住密码，设置session的周期为None，即2周
            request.session.set_expiry(None)
        # 响应登陆结果
        return redirect(reverse('contents:index'))
