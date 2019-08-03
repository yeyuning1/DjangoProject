from django.conf.urls import url

from areas import views

app_name = 'areas'
urlpatterns = [
    url(r'^areas/$', views.ProvinceAreasView.as_view()),
    url(r'^areas/(?P<pk>[1-9]\d+)/$', views.SubAreasView.as_view()),
    url(r'^addresses/$', views.AddressView.as_view()),
    url(r'^addresses/create/$', views.CreateAddressView.as_view()),
    # 修改和删除收货地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
]
