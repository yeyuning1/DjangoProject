from django.conf.urls import url

from contents import views

app_name = 'contents'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]
