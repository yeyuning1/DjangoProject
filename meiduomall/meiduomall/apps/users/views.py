import json
import logging
import re
from django.contrib.auth import login, authenticate, logout
from django.db import DatabaseError
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from celery_tasks.email.tasks import send_verify_email
from meiduomall.utils.response_code import RETCODE
from meiduomall.utils.views import LoginRequiredMixin, LoginRequiredJSONMixin
from .models import User

logger = logging.getLogger('django')


# -------------------------------------------------

class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        """处理注册页面发送的表单请求"""

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
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


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
    """用户登陆"""

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        """验证用户登陆信息"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 检查参数
        if not all([username, password]):
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
        # 获取跳转过来的地址:
        next = request.GET.get('next')
        # 判断参数是否存在:
        if next:
            # 如果是从别的页面跳转过来的, 则重新跳转到原来的页面
            response = redirect(next)
        else:

            # 如果是直接登陆成功，就重定向到首页
            response = redirect(reverse('contents:index'))

        # 设置 cookie 信息
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 返回响应
        return response


# -------------------------------------------------
# 以下为登出

class LogoutView(View):
    '''退出登陆'''

    def get(self, request):
        '''
        实现登出功能，即清除session
        :param request:
        :return:
        '''
        # 清理 session
        logout(request)
        # 重定向到首页
        response = redirect(reverse('contents:index'))
        # 退出登陆时要清除cookie中的uernames
        response.delete_cookie('username')
        # 返回响应体
        return response


# -------------------------------------------------
# 以下为用户个人中心

class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供个人信息界面"""
        # 使用 is_authenticate 判断用户是否登录
        # if request.user.is_authenticated():
        #     return render(request, 'user_center_info.html')
        # else:
        #      return render(request, 'user_center_info.html')
        # 现已使用LoginRequiredMixin扩展类完成验证登陆功能
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


class EmailView(LoginRequiredJSONMixin, View):
    def put(self, request):
        """实现添加邮箱逻辑"""

        # 判断用户是否登录并返回JSON
        # if not request.user.is_authenticated():
        #     return JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
        # pass

        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        # 校验参数
        if not email:
            return HttpResponseForbidden('缺少email参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponseForbidden('email格式不正确')
        # 赋值 email 字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})
        verify_url = request.user.generate_verify_email_url()
        print(verify_url)
        send_verify_email.delay(email, verify_url)  # TODO：邮箱问题异步待解决
        # 响应添加邮箱的结果
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        """实现邮箱验证逻辑"""
        # 接收参数
        token = request.GET.get('token')

        # 检验参数：判断 token 是否为空
        if not token:
            return HttpResponseForbidden('缺少token')

        # 调用上面封装好的方法，将 token 传入
        user = User.check_verify_email_token(token)

        if not user:
            return HttpResponseForbidden('无效的token')

        # 修改 email_active 的值为 True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseForbidden('激活邮件失败')

        # 返回邮箱验证结果
        return redirect(reverse('users:info'))
