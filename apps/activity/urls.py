# coding:utf-8
from django.conf.urls import url
from .views import activity, sign

urlpatterns = [
    url(r'^$', activity.ActivityView.as_view(), name='activity'),
    url(r'^add/$', activity.ActivityAddView.as_view(), name='activity_add'),
    url(r'^edit/(?P<id>\d+)/$', activity.ActivityEditView.as_view(), name='activity_edit'),
    url(r'^delete/$', activity.delete_activity, name='activity_delete'),
    url(r'^getactivities/$', activity.get_activities, name='activity_list'),
    url(r'^selectoractivities/$', activity.selector_activities, name='activity_selector'),

    url(r'^sign/$', sign.SignView.as_view(), name='sign'),
    url(r'^getsigns/$', sign.get_signs, name='sign_list'),

]
