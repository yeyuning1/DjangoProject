import logging

from QQLoginTool.QQtool import OAuthQQ
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from meiduomall import settings
from meiduomall.settings import dev
from meiduomall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token

logger = logging.getLogger('django')


class QQURLView(View):
    """提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?
    response_type=code&
    client_id=xxx&
    redirect_uri=xxx&
    state=xxx
    """

    def get(self, request):
        # 获取 QQ 登录页面网址
        # 创建 OAuthQQ 类的对象
        oauth = OAuthQQ(client_id=dev.QQ_CLIENT_ID,
                        client_secret=dev.QQ_CLIENT_SECRET,
                        redirect_uri=dev.QQ_REDIRECT_URI,
                        state=next)
        # 调用对象的获取qq地址方法
        login_url = oauth.get_qq_url()
        next = request.GET.get('next')
        return JsonResponse({'code': RETCODE.OK,
                             'errmsg': 'OK',
                             'login_url': login_url})


class QQUserView(View):
    """用户扫码登陆的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 提取code请求参数
        code = request.GET.get('code')
        if not code:
            return HttpResponseForbidden('缺少code')

        # 创建工具对象
        oauth = OAuthQQ(client_id=dev.QQ_CLIENT_ID,
                        client_secret=dev.QQ_CLIENT_SECRET,
                        redirect_uri=dev.QQ_REDIRECT_URI,
                        state=next)

        try:
            # 携带 code 向 QQ服务器 请求 access_token
            access_token = oauth.get_access_token(code)

            # 携带 access_token 向 QQ 服务器请求 openid
            openid = oauth.get_open_id(access_token)

        except Exception as e:
            # 获取 openid 失败，验证失败
            logger.error(e)
            # 返回结果
            return HttpResponseServerError('OAuth2.0认证失败')
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果 openid 没绑定美多商城用户
            # 调用方法对 openid 加密，生成 access_token 字符串
            access_token = generate_access_token(openid)
            # 将access_token拼接为字典
            context = {'access_token': access_token}
            # 返回响应，重新渲染
            return render(request, 'oauth_callback.html', context)
        else:
            # 如果 openid 已绑定美多商城用户
            # 根据 user 外键, 获取对应的 QQ用户
            qq_user = oauth_user.user
            # 实现状态保持
            login(request, qq_user)

            # 创建重定向到主页的对象
            response = redirect(reverse('contents:index'))

            # 将用户信息写入到 cookie 中，有效期15天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)

            # 返回响应
            return response

    def post(self, request):
        """用户绑定到openid"""
        pass
        # TODO：
