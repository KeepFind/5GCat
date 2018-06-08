# coding:utf-8
from django.conf.urls import url
from .views import user, group, sms, config, log

urlpatterns = [
    url(r'^user/$', user.UserView.as_view(), name='user'),
    url(r'^user/add/$', user.UserAddView.as_view(), name='user_add'),
    url(r'^user/edit/(?P<id>\d+)/$', user.UserEditView.as_view(), name='user_edit'),
    url(r'^user/delete/$', user.delete_user, name='user_delete'),
    url(r'^user/resetpwd/$', user.UserResetPwdView.as_view(), name='user_resetpwd'),
    url(r'^user/setstatus/$', user.set_status, name='user_setstatus'),
    url(r'^user/getusers/$', user.get_users, name='user_list'),

    url(r'^user/perm/(?P<id>\d)/$', user.UserPermView.as_view(), name='user_perm'),  # 授权
    url(r'^group/$', group.GroupView.as_view(), name='group'),
    url(r'^group/add/$', group.GroupAddView.as_view(), name='group_add'),
    url(r'^group/edit/(?P<id>\d+)/$', group.GroupEditView.as_view(), name='group_edit'),
    url(r'^group/delete/$', group.delete_group, name='group_delete'),
    url(r'^group/getgroups/$', group.get_groups, name='group_list'),

    url(r'^sms/$', sms.SmsView.as_view(), name='sms'),
    url(r'^sms/detail/(?P<id>\d+)/$', sms.SmsDetailView.as_view(), name='sms_detail'),
    url(r'^getsms/$', sms.get_sms, name='sms_list'),

    url(r'^log/$', log.LogView.as_view(), name='log'),
    url(r'^getlogs/$', log.get_logs, name='log_list'),

    url(r'^config/$', config.ConfigView.as_view(), name='config'),
    url(r'^config/edit/$', config.ConfigEditView.as_view(), name='config_edit'),
]
