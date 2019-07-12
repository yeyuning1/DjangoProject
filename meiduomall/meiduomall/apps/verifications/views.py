from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from verifications import crons


class ImageCodeView(View):
    def get(self, request, uuid):
        # TODO:生成验证码图片和文本
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('image_code_%s' % uuid, crons.IMAGE_CODE_EXPIRE, text)
        return HttpResponse(image, content_type='image/jpg')
