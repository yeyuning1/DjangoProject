from django.conf.urls import url, include

from orders import views

app_name = 'orders'
urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view(), name='info'),
    url(r'^orders/comment/(?P<order_id>\d+)/$', views.OrderCommentView.as_view()),
    url(r'^orders/comment/$', views.OrderCommentView.as_view()),
]
