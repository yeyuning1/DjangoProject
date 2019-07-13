from QQLoginTool.QQtool import OAuthQQ
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from meiduomall import settings
from meiduomall.utils.response_code import RETCODE


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
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        # 调用对象的获取qq地址方法
        login_url = oauth.get_qq_url()
        next = request.GET.get('next')
        return JsonResponse({'code': RETCODE.OK,
                             'errmsg': 'OK',
                             'login_url': login_url})
