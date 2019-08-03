# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
from celery_tasks.yuntongxun.ccp_sms import CCP
from celery_tasks.main import celery_app
import logging

logger = logging.getLogger('django')


@celery_app.task(bind=True, name='ccp_send_sms_code', retry_backoff=3)
def ccp_send_sms_code(self, mobile, sms_code):
    """
    发送短信异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功0 或 失败-1
    """

    try:
        # 调用 CCP() 发送短信, 并传递相关参数:
        result = CCP().send_template_sms(mobile,
                                         [sms_code, 5],
                                         1)

    except Exception as e:
        # 如果发送过程出错, 打印错误日志
        logger.error(e)

        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)

    # 如果发送成功, rend_ret 为 0:
    if result != 0:
        # 有异常自动重试三次
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)

    return result
# ccp_send_sms_code.delay(mobile, sms_code)


# 开启协程模式
# > celery -A celery_tasks.main worker -l info -P eventlet -c 1000
