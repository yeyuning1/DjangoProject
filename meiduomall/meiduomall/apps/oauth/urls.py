from django.conf.urls import url

from oauth import views

app_name = 'oauth'
urlpatterns = [  # 获取QQ扫码登录链接
    url(r'^qq/authorization/$', views.QQURLView.as_view()),
]
