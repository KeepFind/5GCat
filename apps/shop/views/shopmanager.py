import json
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from common.string_extension import safe_dict_value, cast_endtime
from manage.signals import post_logic_delete
from shop.forms import ShopEditForm, ShopManagerAddForm
from shop.models import Shop, AuthShopManager
from user.forms import UserEditForm, UserAddForm
from user.models import User, UserInfo


class ShopManagerView(PermissionRequiredMixin, View):
    template_name = 'shop/shopmanager.html'
    permission_required = ('shop.view_shopmanager')

    def get(self, request, *args, **kwargs):
        shopNo = request.GET.get('shopNo')
        context = Shop.objects.get_id_name(shopNo)
        return render(request, self.template_name, context)


class ShopManagerAddView(PermissionRequiredMixin, View):
    template_name = 'shop/shopmanager_add.html'
    permission_required = ('shop.add_shopmanager')

    def get(self, request, *args, **kwargs):
        form = ShopManagerAddForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ShopManagerAddForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.updatedUser = request.user.username
        model.password = make_password(form.cleaned_data.get('password'))
        model.is_active = True
        model.is_superuser = True
        model.is_staff = True
        model.save()

        return redirect('shop:shopmanager')


# class ShopManagerEditView(View):
#     template_name = 'shop/shopmanager_edit.html'
#     permission_required = ('user.change_user')
#
#     def get(self, request, *args, id):
#         user = get_object_or_404(User, userId=id)
#         form = UserEditForm(instance=user)
#         return render(request, self.template_name, {'form': form})
#
#     def post(self, request, *args, id):
#         user = get_object_or_404(Shop, shopId=id)
#         form = UserEditForm(request.POST, instance=user)
#         if not form.is_valid():
#             errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
#             return render(request, self.template_name, {'error': errors, 'form': form})
#
#         model = form.save(commit=False)
#         model.save()
#
#         return redirect('shop:shopmanager')


def get_shopmanagers(request):
    ''' 获取门店管理员列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    shopNo = request.GET.get('shopNo')
    registerStart = request.GET.get('registerStart')
    registerEnd = request.GET.get('registerEnd')

    users = AuthShopManager.objects.filter(is_staff=True)
    if shopNo:
        users = users.filter(shopNo=shopNo)
    if registerStart:
        users = users.filter(date_joined__gte=registerStart)
    if registerEnd:
        users = users.filter(date_joined__lt=cast_endtime(registerEnd))

    count = users.count()  # 总数
    mgrs = users.order_by('-date_joined')[(page - 1) * pagesize:page * pagesize]

    shopNo_list = [item.shopNo for item in mgrs]
    shops = Shop.objects.filter(fiveSysId__in=shopNo_list).values('fiveSysId', 'shopName')

    result = []
    for item in mgrs:
        shopName = safe_dict_value(list(filter(lambda m: m['fiveSysId'] == item.shopNo, shops)), 'shopName')
        result.append(item.to_dict(shopName))

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


@csrf_exempt
@permission_required2('shop.delete_auth_shopmanager')
@require_http_methods(['POST'])
def delete_shopmanager(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        AuthShopManager.objects.filter(id__in=ids).update(is_staff=False)
        post_logic_delete.send(sender='delete_auth_shopmanager', app_label='shop', model_name='auth_shopmanager',
                               ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()
