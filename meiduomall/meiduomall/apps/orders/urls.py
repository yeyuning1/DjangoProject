from django.conf.urls import url, include

from orders import views

app_name = 'orders'
urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
]
