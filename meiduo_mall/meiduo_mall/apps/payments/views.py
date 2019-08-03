from django.shortcuts import render
from django.views import View
from django import http
from alipay import AliPay
from django.conf import settings
import os
from orders.models import OrderInfo
from .models import Payment

from meiduo_mall.utils.response_code import RETCODE


class GetUrlView(View):
    def get(self, request, order_id):
        # 验证订单编号
        try:
            order = OrderInfo.objects.get(pk=order_id)
        except:
            return http.Http404('订单编号无效')
        # 创建支付宝对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(settings.BASE_DIR, 'libs/alipay/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'libs/alipay/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # 生成支付的参数
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='美多商城在-订单支付',
            return_url=settings.ALIPAY_RETURN_URL
        )
        # 拼接最终的支付地址
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        # 响应
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'alipay_url': alipay_url
        })


class AlipayStatusView(View):
    def get(self, request):
        # 接收支付宝返回的数据
        data = request.GET.dict()
        # print(data)
        '''
        {
            'version': '1.0',
            'method': 'alipay.trade.page.pay.return',
            'app_id': '2016082100304973',
            'total_amount': '18550.00',
            'sign_type': 'RSA2',
            'trade_no': '2019040222001420411000002830', #支付宝为这个订单生成的唯一标识
            'sign': 'KNt4aaw1gpNMngBkYgjJxBguwzo7+ac2mNPcl1/BfbIJlMhL25D9L7oLyLDZvygGnLBP4S9fwhc7BCDz//CXsGudddNtWptKOueVudEm2N5JQ+JitHFm/TiDs/IuPDu2TD9JgBPQsNMGa6WmB/7IFqoKmyHlRcl3b4UT+KzaeR9SV5gkbFuZRad9pTHxQ0+RJo3XaqDXHqAvKoDzEmex6OIz/979uGGK1O7C43Ga1kQpYfTPldWK9CMgaHPPzvrJEtosb2ZhgpQbPrUxkTqlcMSlX6Icn+1ZoWPM1t4oZ44l3x+AdGMyx/3KaWfpYHw2/UGbrPDksnXC5UR8FbVJSg==',
            'out_trade_no': '20190402031224000000001', #订单编号
            'timestamp': '2019-04-02 12:26:15',
            'auth_app_id': '2016082100304973',
            'charset': 'utf-8',
            'seller_id': '2088102172415825'
        }
        '''
        signature = data.pop('sign')

        # 验证是否支付成功
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(settings.BASE_DIR, 'libs/alipay/app_private_key.pem'),
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'libs/alipay/alipay_public_key.pem'),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        success = alipay.verify(data, signature)

        if not success:
            # 如果支付失败，则提示
            return http.HttpResponseBadRequest('支付失败，订新支付')

        # 如果支付成功，则修改订单的状态
        order_id = data.get('out_trade_no')
        trade_no = data.get('trade_no')
        # 1.保存支付宝流水号
        Payment.objects.create(
            order_id=order_id,
            trade_id=trade_no
        )
        # 2.修改订单状态为待发货
        OrderInfo.objects.filter(pk=order_id).update(status=1)

        context = {
            'trade_no': data.get('trade_no')
        }

        return render(request, 'pay_success.html', context)
