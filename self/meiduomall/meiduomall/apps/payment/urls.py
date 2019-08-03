from django.conf.urls import url, include

from payment import views

app_name = 'payment'
urlpatterns = [
    url(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    url(r'^payment/status/$', views.PaymentStatusView.as_view()),
]
