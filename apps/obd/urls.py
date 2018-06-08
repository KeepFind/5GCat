# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ObdView.as_view(), name='obd'),
    url(r'^add/$', views.ObdAddView.as_view(), name='obd_add'),
    url(r'^delete/$', views.delete_obd, name='obd_delete'),
    url(r'^getobds/$', views.get_obds, name='obd_list'),
]
