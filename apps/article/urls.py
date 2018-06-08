# coding:utf-8
from django.conf.urls import url
from .views import headline

urlpatterns = [
    url(r'^headline/$', headline.HeadlineView.as_view(), name='headline'),
    url(r'^headline/add/$', headline.HeadlineAddView.as_view(), name='headline_add'),
    url(r'^headline/edit/(?P<id>\d+)/$', headline.HeadlineEditView.as_view(), name='headline_edit'),
    url(r'^headline/delete/$', headline.delete_headline, name='headline_delete'),
    url(r'^headline/setstatus/$', headline.set_status, name='headline_setstatus'),
    url(r'^getheadlines/$', headline.get_headlines, name='headline_list'),
]
