from django.conf.urls import url

from users import views

app_name = 'users'
urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
]
