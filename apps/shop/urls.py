# coding:utf-8
from django.conf.urls import url
from .views import shop, shopmanager

urlpatterns = [
    url(r'^shop/$', shop.ShopView.as_view(), name='shop'),
    url(r'^add/$', shop.ShopAddView.as_view(), name='shop_add'),
    url(r'^edit/(?P<shopNo>\w+)/$', shop.ShopEditView.as_view(), name='shop_edit'),
    url(r'^delete/$', shop.delete_shop, name='shop_delete'),
    url(r'^delete/shopimg/$', shop.delete_shopimg, name='shopimg_delete'),
    url(r'^getshops/$', shop.get_shops, name='shop_list'),
    url(r'^getshopimgs/$', shop.get_shopimgs, name='shopimg_list'),

    url(r'^selectorshops/$', shop.selector_shops, name='shop_selector'),

    url(r'^shopmanager/$', shopmanager.ShopManagerView.as_view(), name='shopmanager'),
    url(r'^shopmanager/add/$', shopmanager.ShopManagerAddView.as_view(), name='shopmanager_add'),
    # url(r'^shopmanager/edit/(?P<id>\d+)/$', shopmanager.ShopManagerEditView.as_view(), name='shopmanager_edit'),
    url(r'^shopmanager/delete/$', shopmanager.delete_shopmanager, name='shopmanager_delete'),

    url(r'^getshopmanagers/$', shopmanager.get_shopmanagers, name='shopmanager_list'),
]
