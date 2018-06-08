# coding:utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ueditor/$', views.ueditor, name='ueditor'),

    url(r'^saveimage/$', views.save_image, name='save_image'),
]
