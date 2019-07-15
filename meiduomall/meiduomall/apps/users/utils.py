# 增加多账号登陆功能
from django.contrib.auth.backends import ModelBackend
import re
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from meiduomall.utils.response_code import RETCODE
from users.models import User
from django.utils.decorators import wraps


def get_user_by_account(account):
    """
    根据account查询用户
    :param account: 用户名或者手机号
    :return: user
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 手机号登录
            user = User.objects.get(mobile=account)
        else:
            # 用户名登录
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


def login_required_json(view_func):
    """
    判断用户是否登录的装饰器，并返回 json
    :param view_func: 被装饰的视图函数
    :return: json、view_func
    """

    # 恢复 view_func 的名字和文档
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # 如果用户未登录，返回 json 数据
        if not request.user.is_authenticated():
            return JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})
        else:
            # 如果用户登录，进入到 view_func 中
            return view_func(request, *args, **kwargs)

    return wrapper


class UsernameMobileAuthBackend(ModelBackend):
    '''自定义用户认证后端'''

    def authenticate(self, request, username=None, password=None, **kwargs):
        '''
        重写认值方法，实现用户名和mobile登陆功能
        :param request:
        :param username:
        :param password:
        :param kwargs:
        :return:
        '''
        # 自定义验证用户是否存在的函数:
        # 根据传入的 username 获取 user 对象
        # username 可以是手机号也可以是账号
        user = get_user_by_account(username)
        # 校验user是否存在并校验密码是否正确
        if user and user.check_password(password):
            return user


class LoginRequiredMixin(object):
    """验证用户是否登陆的扩展类"""

    @classmethod
    def as_view(cls, **initkwargs):
        # 调用mro继承顺序上的as_view()函数
        view = super().as_view()
        return login_required(view)


class LoginRequiredJSONMixin(object):
    """验证用户是否登陆并返回 json 的扩展类"""

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required_json(view)
