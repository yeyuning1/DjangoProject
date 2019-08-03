from django.conf.urls import url

from contents import views

app_name = 'contents'
urlpatterns = [
    # 商品列表页
    url(r'^$', views.IndexView.as_view(), name='index'),
]
