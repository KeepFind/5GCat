# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^all/$', views.StatsAllView.as_view(), name='stats_all'),
    url(r'^detail/(?P<id>\d+)/$', views.StatsDetailView.as_view(), name='stats_detail'),
    url(r'^getallstats/$', views.get_all_stats, name='stats_all_list'),

    url(r'^shop/$', views.StatsShopView.as_view(), name='stats_shop'),
    url(r'^getshopstats/$', views.get_shop_stats, name='stats_shop_list'),
]
