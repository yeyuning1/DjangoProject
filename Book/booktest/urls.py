from django.conf.urls import url
from rest_framework.routers import DefaultRouter, SimpleRouter

from booktest import views

urlpatterns = [
]
# 路由Router: 动态生成视图集中处理函数的url配置项
# router = SimpleRouter()
router = DefaultRouter()  # 路由Router
router.register('books', views.BookInfoViewSet, base_name='books')  # 向路由Router中注册视图集

urlpatterns += router.urls  # 将路由Router生成的url配置信息添加到django的路由列表中
