from django.conf.urls import url

from rest_framework.routers import DefaultRouter

from meiduo_admin.views import skus, spus, orders, permissions, specs
from .views import channels
from .views import statistical
from .views import users

urlpatterns = [
    url(r'^authorizations/$', users.AdminAuthorizeView.as_view()),
    url(r'^statistical/total_count/$', statistical.UserTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistical.UserDayIncrementView.as_view()),
    url(r'^statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    url(r'^statistical/day_orders/$', statistical.UserDayOrdersView.as_view()),
    url(r'^statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    url(r'^statistical/goods_day_views/$', statistical.GoodsDayView.as_view()),
    url(r'^users/$', users.UserInfoView.as_view()),
    url(r'^goods/channel_types/$', channels.ChannelTypesView.as_view()),
    url(r'^goods/categories/$', channels.ChannelCategoriesView.as_view()),
    url(r'^goods/channel/categories/$', spus.GoodsCategoriesView.as_view()),
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spus.GoodsCategorySubsView.as_view()),
    url(r'^goods/brands/simple/$', spus.BrandsSimpleView.as_view()),
    url(r'^skus/simple/$', skus.SKUSimpleView.as_view()),
    url(r'^goods/simple/$', spus.SPUSimpleView.as_view()),
    url(r'^goods/(?P<pk>\d+)/specs/$', spus.SPUSpecView.as_view()),
    url(r'^permission/content_types/$', permissions.PermissionViewSet.as_view({
        'get': 'content_types'
    })),
    url(r'^permission/simple/$', permissions.GroupViewSet.as_view({
        'get': 'simple'
    })),
    url(r'^permission/groups/simple/$', permissions.AdminViewSet.as_view({
        'get': 'simple'
    })),
]
router = DefaultRouter()
router.register('goods/channels', channels.ChannelViewSet, base_name='channels')
urlpatterns += router.urls
router = DefaultRouter()
router.register(r'skus/images', skus.SKUImageViewSet, base_name='images')
urlpatterns += router.urls
router = DefaultRouter()
router.register('skus', skus.SKUViewSet, base_name='skus')
urlpatterns += router.urls
# 规格管理视图
router = DefaultRouter()
router.register('goods/specs', specs.SpecsViewSet, base_name='admins')
urlpatterns += router.urls
# SPU管理
router = DefaultRouter()
router.register('goods', spus.SPUViewSet, base_name='goods')
urlpatterns += router.urls
# 订单管理
router = DefaultRouter()
router.register('orders', orders.OrdersViewSet, base_name='orders')
urlpatterns += router.urls
# 权限管理
router = DefaultRouter()
router.register('permission/perms', permissions.PermissionViewSet, base_name='perms')
urlpatterns += router.urls

router = DefaultRouter()
router.register('permission/groups', permissions.GroupViewSet, base_name='groups')
urlpatterns += router.urls
router = DefaultRouter()
router.register('permission/admins', permissions.AdminViewSet, base_name='admins')
urlpatterns += router.urls
