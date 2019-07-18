from django.conf.urls import url

from users import views

app_name = 'users'
urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    url(r'usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^emails/$', views.EmailView.as_view()),
    url(r'^addresses/$', views.AddressView.as_view(), name='addresses'),
    url(r'^password/$', views.ChangePasswordView.as_view(), name='pass'),
]
