from django.conf.urls import url
from . import views

urlpatterns = [
    url('^orders/settlement/$', views.SettlementView.as_view()),
    url('^orders/commit/$', views.CommitView.as_view()),
    url('^orders/success/$', views.SuccessView.as_view()),
    url('^orders/info/(?P<page_num>\d+)/$', views.InfoView.as_view()),
    url('^orders/comment/$', views.CommentView.as_view()),
    url('^comment/(?P<sku_id>\d+)/$', views.CommentSKUView.as_view()),
]
