from django.conf.urls import url

from verifications import views

app_name = 'verifications'
urlpatterns = [
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view())
]
