import logging

from django.core.mail import send_mail

from celery_tasks.main import celery_app
from meiduomall.settings import dev

logger = logging.getLogger('django')


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """
    发送验证邮箱邮件
    :param to_mail: 收件人邮箱
    :param verify_url: 验证链接
    :return: None
    """

    # 标题
    subject = '邮箱验证'
    # 发送内容
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        # 进行发送
        send_mail(subject, "", dev.EMAIL_FROM, [to_email], html_message)

    except Exception as e:
        logger.error(e)
        # 有异常自动尝试三次
        raise self.retry(exc=e, max_retries=3)
