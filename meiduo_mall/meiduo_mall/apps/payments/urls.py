from django.conf.urls import url
from . import views

urlpatterns = [
    url('^payment/(?P<order_id>\d+)/$', views.GetUrlView.as_view()),
    url('^payment/status/$', views.AlipayStatusView.as_view()),
]
