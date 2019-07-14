import os

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'
# 导入 Celery 类

from celery import Celery

# 创建 celery 对象
celery_app = Celery('meiduo')

# 给 celery 添加配置
celery_app.config_from_object('celery_tasks.config')

# 让 celery_app 自动捕获目标地址下的任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
