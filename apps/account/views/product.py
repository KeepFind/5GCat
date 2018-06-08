# coding:utf-8
import json
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from account.forms import ProductForm
from account.models import PayInfo
from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from manage.signals import post_logic_delete


class ProductView(PermissionRequiredMixin,View):
    template_name = 'account/product.html'
    permission_required = ('account.view_payinfo')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ProductAddView(PermissionRequiredMixin, View):
    template_name = 'account/product_add.html'
    permission_required = ('account.add_payinfo')

    def get(self, request, *args, **kwargs):
        form = ProductForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.status = (int(form.cleaned_data.get('activate_status')) << 1)
        model.createdUser = request.user.username
        model.updatedUser = request.user.username
        model.save()

        return redirect('account:product')


class ProductEditView(PermissionRequiredMixin, View):
    template_name = 'account/product_edit.html'
    permission_required = ('account.chagne_payinfo')

    def get(self, request, *args, id):
        product = get_object_or_404(PayInfo, piId=id)
        form = ProductForm(instance=product)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        product = get_object_or_404(PayInfo, piId=id)
        form = ProductForm(request.POST, instance=product)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.status = (int(form.cleaned_data.get('activate_status')) << 1) + (model.status & 1)
        model.updatedUser = request.user.username
        model.save()

        return redirect('account:product')


@csrf_exempt
@permission_required2('account.delete_payinfo')
@require_http_methods(['POST'])
def delete_product(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')
        # 逻辑删除
        PayInfo.objects.filter(piId__in=ids).update(status=F('status').bitand(2) + 1)
        post_logic_delete.send(sender='delete_product', app_label='account', model_name='payinfo', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！')
    return JSONResponse()


def get_products(request):
    ''' 获取产品列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    keyword = request.GET.get('keywords')

    products = PayInfo.objects.all()
    if keyword:
        products = products.filter(username__contains=keyword)  # 按名称查询
    count = products.count()  # 总数
    users = products.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in users]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
