from django.conf.urls import url

from verifications import views

app_name = 'verifications'
urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SendSmsCodeView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),

]
