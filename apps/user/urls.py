# coding:utf-8
from django.conf.urls import url
from .views import user, car, carbrand

urlpatterns = [
    url(r'^index/$', user.UserView.as_view(), name='user'),
    url(r'^edit/(?P<id>\d+)/$', user.UserEditView.as_view(), name='user_edit'),
    url(r'^detail/(?P<id>\d+)/$', user.UserDetailView.as_view(), name='user_detail'),
    url(r'^delete/$', user.delete_user, name='user_delete'),
    url(r'^setstatus/$', user.set_status, name='user_setstatus'),
    url(r'^getusers/$', user.get_users, name='user_list'),
    url(r'^selectorusers/$', user.selector_users, name='user_selector'),

    url(r'^car/$', car.CarView.as_view(), name='car'),
    url(r'^car/detail/(?P<id>\d+)/$', car.CarDetailView.as_view(), name='car_detail'),
    url(r'^getcars/$', car.get_cars, name='car_list'),

    url(r'^brand/$', carbrand.CarBrandView.as_view(), name='brand'),
    url(r'^getbrands/$', carbrand.get_carbrands),
    url(r'^getseries/$', carbrand.get_carseries),
    url(r'^getmodels/$', carbrand.get_carmodels)
]
