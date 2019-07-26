import random
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from scripts import captcha
from scripts import RETCODE
from users.models import User
from verifications import constants
import logging

logger = logging.getLogger('django')


class ImageCodeView(View):
    '''
    生成图形验证码
    '''

    def get(self, request, uuid):
        '''
        :param request:
        :param uuid: 用户身份识别码
        :return: image/jpg
        '''
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('image_code_%s' % uuid, constants.IMAGE_CODE_EXPIRE, text)
        return HttpResponse(image, content_type='image/jpg')


class SendSmsCodeView(View):
    def get(self, request, mobile):
        '''
        :param request:
        :param mobile: 手机号码
        :return: JSON
        '''

        # 1.接收参数
        image_code_cli = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2.校验参数
        if not all([image_code_cli, uuid]):
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR,
                                 'errmsg': '缺少必传参数'})
        # 检查是否频繁发送短信验证码请求
        # 连接redis
        redis_conn = get_redis_connection('verify_code')
        # 检查send_flag
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return JsonResponse({{'code': RETCODE.THROTTLINGERR,
                                  'errmsg': '发送短信过于频繁'}})

        # 3.从redis中取得图形验证码
        image_code_server = redis_conn.get('image_code_%s' % uuid)

        # 4.对比、校验图形验证码
        if image_code_server is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR,
                                 'errmsg': '图形验证码失效'})
        if image_code_server.decode().lower() != image_code_cli.lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR,
                                 'errmsg': '图形验证码错误'})

        # 删除有风险，打印错误日志
        try:
            redis_conn.delete('image_code_%s' % uuid)
        except Exception as e:
            logger.error(e)

        # 5.发送手机短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # logger.info(sms_code)
        print(sms_code)

        # 使用容联云平台给用户发送短信
        # CCP().send_template_sms(mobile,
        #                         [sms_code, constants.SMS_CODE_EXPIRE_M], constants.SMS_CODE_EXPIRE_TEMPLATES)
        # 使用Celery进行异步短信发送
        # ccp_send_sms_code.delay(mobile, sms_code)
        # 使用pipeline操作Redis数据库
        # 1. 创建Redis管道
        # 2. 将Redis请求添加到队列
        # 3. 执行请求
        # 保存手机验证码
        pl = redis_conn.pipeline()
        pl.setex('sms_code_%s' % mobile, constants.SMS_CODE_EXPIRE_S, sms_code)
        # 重新写入send_flag
        # 60s内是否重复发送的标记
        # SEND_SMS_CODE_INTERVAL = 60
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


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
