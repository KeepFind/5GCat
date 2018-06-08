# coding:utf-8
from django.conf.urls import url
from .views import ad, adposition

urlpatterns = [
    url(r'^$', ad.AdView.as_view(), name='ad'),
    url(r'^add/(?P<ad_type>\w+)/$', ad.AdAddView.as_view(), name='ad_add'),
    url(r'^edit/(?P<id>\d+)/$', ad.AdEditView.as_view(), name='ad_edit'),
    url(r'^delete/$', ad.delete_ad, name='ad_delete'),
    url(r'^getadlist/$', ad.get_ads, name='ad_list'),

    url(r'^adposition/$', adposition.AdPositionView.as_view(), name='adposition'),
    url(r'^adposition/add/$', adposition.AdPositionAddView.as_view(), name='adposition_add'),
    url(r'^adposition/delete/$', adposition.delete_adposition, name='adposition_delete'),
    url(r'^adposition/setstatus/$', adposition.set_status, name='adposition_setstatus'),
    url(r'^getadpositions/$', adposition.get_adpositions, name='adposition_list'),
    url(r'^selectoradpositions/$', adposition.selector_adpositions, name='adposition_selector'),
]
