# coding:utf-8
from django.conf.urls import url
from .views import account, product

urlpatterns = [
    url(r'^payorder/$', account.PayOrderView.as_view(), name='payorder'),
    url(r'^getpayorders/$', account.get_payorders, name='payorder_list'),

    url(r'^payorder/detail/(?P<orderno>\d+)/$', account.PayOrderDetailView.as_view(), name='payorder_detail'),

    url(r'^withdraworder/$', account.WithdrawOrderView.as_view(), name='withdraworder'),
    url(r'^withdraworder/detail/(?P<id>\d+)/$', account.WithdrawOrderDetailView.as_view(), name='payorder_detail'),
    url(r'^withdraworder/audit/$', account.audit_withdraworder, name='withdraworder_audit'),  # 提现审核
    url(r'^getwithdraworders/$', account.get_withdraworders, name='withdraworder_list'),

    url(r'^awardrecord/$', account.AwardRecordView.as_view(), name='awardrecord'),
    url(r'^getawardrecords/$', account.get_awardrecords, name='awardrecord_list'),

    url(r'^product/$', product.ProductView.as_view(), name='product'),
    url(r'^product/add/$', product.ProductAddView.as_view(), name='product_add'),
    url(r'^product/edit/(?P<id>\d+)/$', product.ProductEditView.as_view(), name='product_edit'),
    url(r'^product/delete/$', product.delete_product, name='product_delete'),
    url(r'^getproducts/$', product.get_products, name='product_list'),
]
