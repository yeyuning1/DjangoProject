from django.conf.urls import url

from carts import views

app_name = 'carts'
urlpatterns = [
    # 购物车查询和新增和修改和删除
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
    url(r'^carts/simple/$', views.CartsSimpleView.as_view()),
    url(r'^carts/selection/$', views.CartSelectAllView.as_view()),
]
