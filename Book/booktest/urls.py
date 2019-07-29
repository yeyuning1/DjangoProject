from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from booktest import views

urlpatterns = [
    # url(r'^books/$', views.BookListView.as_view()),
    # url(r'^books/(?P<pk>\d+)/$', views.BookDetailView.as_view())
]
# 路由Router: 动态生成视图集中处理函数的url配置项
router = DefaultRouter()  # 路由Router
router.register('books', views.BookInfoViewSet)  # 向路由Router中注册视图集

urlpatterns += router.urls  # 将路由Router生成的url配置信息添加到django的路由列表中
