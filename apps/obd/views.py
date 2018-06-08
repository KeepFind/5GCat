import json

from django.contrib.auth.mixins import PermissionRequiredMixin
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
from common.string_extension import cast_endtime, safe_dict_value, safe_dict_values
from manage.signals import post_logic_delete
from obd.forms import ObdAddForm
from obd.models import ObdDevice, CarObd
from shop.forms import ShopEditForm
from shop.models import Shop
from shop.service import save_shop
from user.models import CarInfo


class ObdView(PermissionRequiredMixin, View):
    template_name = 'obd/obd.html'
    permission_required = ('shop.view_shop')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ObdAddView(PermissionRequiredMixin, View):
    template_name = 'obd/obd_add.html'
    permission_required = ('shop.add_user')

    def get(self, request, *args, **kwargs):
        form = ObdAddForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ObdAddForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        form.save()
        return redirect('obd:obd')


class ObdEditView(PermissionRequiredMixin, View):
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


@csrf_exempt
# @permission_required2('shop.delete_shop')
@require_http_methods(['POST'])
def delete_obd(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        ObdDevice.objects.filter(sn__in=ids).delete()
        post_logic_delete.send(sender='delete_obd', app_label='obd', model_name='obddevice', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()


def get_obds(request):
    ''' 获取obd设备列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    sn = request.GET.get('sn')
    purchaseTime = request.GET.get('purchaseTime')
    purchaseTimeEnd = request.GET.get('purchaseTimeEnd')

    obds = ObdDevice.objects.all()
    if sn:
        obds = obds.filter(sn__contains=sn)
    if purchaseTime:
        obds = obds.filter(purchaseTime__gt=purchaseTime)
    if purchaseTimeEnd:
        obds = obds.filter(purchaseTime__lt=cast_endtime(purchaseTimeEnd))

    count = obds.count()  # 总数
    obds = obds.order_by('-purchaseTime')[(page - 1) * pagesize:page * pagesize]

    obd_sns = [item.sn for item in obds]
    car_obds = CarObd.objects.filter(sn__in=obd_sns).values('sn', 'shopNo', 'carId')  #车辆obd关联数据

    shopNo_list = []
    carId_list = []
    for item in car_obds:
        shopNo_list.append(item['shopNo'])
        carId_list.append(item['carId'])

    shops = Shop.objects.filter(fiveSysId__in=shopNo_list).values('fiveSysId', 'shopName')
    cars = CarInfo.objects.filter(carId__in=carId_list).values('carId', 'carNoFix', 'carNo')

    result = []
    for obd in obds:
        d1 = safe_dict_values(list(filter(lambda m: m['sn'] == obd.sn, car_obds)), 'shopNo', 'carId')
        d2 = safe_dict_values(list(filter(lambda m: m['carId'] == d1['carId'], cars)), 'carNoFix', 'carNo')
        shopName = safe_dict_value(list(filter(lambda m: m['fiveSysId'] == d1['shopNo'], shops)), 'shopName')

        result.append(obd.to_dict(d1['shopNo'], shopName, d1['carId'], d2['carNoFix'] , d2['carNo']))

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
