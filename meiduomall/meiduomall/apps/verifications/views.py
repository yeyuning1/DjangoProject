import random
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from libs.yuntongxun.ccp_sms import CCP
from utils.response_code import RETCODE
from verifications import crons
import logging

logger = logging.Logger('django')


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
        redis_conn.setex('image_code_%s' % uuid, crons.IMAGE_CODE_EXPIRE, text)
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
            return JsonResponse({{'code': RETCODE.NECESSARYPARAMERR,
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
        #                         [sms_code, crons.SMS_CODE_EXPIRE_M], crons.SMS_CODE_EXPIRE_TEMPLATES)

        # 保存手机验证码
        redis_conn.setex('sms_code_%s' % mobile, crons.SMS_CODE_EXPIRE_S, sms_code)
        # 重新写入send_flag
        # 60s内是否重复发送的标记
        # SEND_SMS_CODE_INTERVAL = 60
        redis_conn.setex('send_flag_%s' % mobile, crons.SEND_SMS_CODE_INTERVAL, 1)
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
