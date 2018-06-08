import json
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
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
from common.string_extension import cast_endtime
from common.upload import qiniu_upload
from manage.signals import post_logic_delete
from shop.forms import ShopEditForm
from shop.models import Shop, ShopImg
from shop.service import save_shop


class ShopView(PermissionRequiredMixin, View):
    template_name = 'shop/shop.html'
    permission_required = ('shop.view_shop')

    def get(self, request, *args, **kwargs):
        shopNo = request.GET.get('shopNo')
        context = Shop.objects.get_id_name(shopNo)
        return render(request, self.template_name, context)


class ShopAddView(PermissionRequiredMixin, View):
    template_name = 'shop/shop_add.html'
    permission_required = ('shop.add_user')

    def get(self, request, *args, **kwargs):
        form = ShopEditForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ShopEditForm(request.POST)
        files = request.FILES.getlist('image')
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.status = 0
        model.createdUser = request.user.username
        model.updatedUser = request.user.username

        is_success = save_shop(model, files)
        if not is_success:
            return render(request, self.template_name, {'error': {'image': '保存失败'}, 'form': form})

        return redirect('shop:shop')


class ShopEditView(PermissionRequiredMixin, View):
    template_name = 'shop/shop_edit.html'
    permission_required = ('shop.change_shop')

    def get(self, request, *args, shopNo):
        shop = get_object_or_404(Shop, fiveSysId=shopNo)
        form = ShopEditForm(instance=shop)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, shopNo):
        shop = get_object_or_404(Shop, fiveSysId=shopNo)
        files = request.FILES.getlist('image')
        form = ShopEditForm(request.POST, instance=shop)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.updatedUser = request.user.username

        is_success = save_shop(model, files)
        if not is_success:
            return render(request, self.template_name, {'error': {'image': '保存失败'}, 'form': form})

        return redirect('shop:shop')


def get_shops(request):
    ''' 获取门店列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    shopNo = request.GET.get('shopNo')
    createStart = request.GET.get('createStart')
    createEnd = request.GET.get('createEnd')

    shops = Shop.objects.all()
    if shopNo:
        shops = shops.filter(fiveSysId=shopNo)
    if createStart:
        shops = shops.filter(createdTime__gte=createStart)
    if createEnd:
        shops = shops.filter(createdTime__lt=cast_endtime(createEnd))

    count = shops.count()  # 总数
    shops = shops.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in shops]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


def get_shopimgs(request):
    ''' 获取门店图片列表 '''
    shopId = request.GET.get('shopId')

    shop = Shop.objects.get(shopId=shopId)
    shopImgs = list(shop.shopimg_set.filter(status=0).values('imgId', 'imgUrl'))

    result = json.dumps(shopImgs)
    return JSONResponse(result)


@csrf_exempt
@permission_required2('shop.delete_shop')
@require_http_methods(['POST'])
def delete_shop(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        Shop.objects.filter(shopId__in=ids).update(status=1, updatedUser=request.user.username)
        post_logic_delete.send(sender='delete_shop', app_label='shop', model_name='shop', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()


@csrf_exempt
@require_http_methods(['POST'])
def delete_shopimg(request):
    try:
        imgId = request.POST.get('imgId')
        shopId = request.POST.get('shopId')

        ShopImg.objects.filter(imgId=imgId).update(status=1)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()


def selector_shops(request):
    '''门店选择下拉框'''
    shopName = request.GET.get('shopName', '')
    if not shopName:
        return JsonResponse({'value': []}, safe=False)

    shops = Shop.objects.filter(shopName__contains=shopName).values('fiveSysId', 'shopName')
    results = {'value': [{'shopNo': item['fiveSysId'], 'shopName': item['shopName']} for item in shops]}

    return JsonResponse(results, safe=False)
