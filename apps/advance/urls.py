# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.AdvanceView.as_view(), name='advance'),
    url(r'^detail/(?P<id>\d+)/$', views.AdvanceDetailView.as_view(), name='advance_detail'),
    url(r'^getadvances/$', views.get_advances, name='advance_list'),
]
