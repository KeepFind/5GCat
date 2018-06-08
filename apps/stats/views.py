import json
from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.decorators import permission_required2
from common.response import paged_result
from common.string_extension import safe_dict_value
from shop.models import Shop
from stats.models import ReceiveMoney


class StatsAllView(PermissionRequiredMixin, View):
    template_name = 'stats/stats_all.html'
    permission_required = ('shop.view_shop')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class StatsDetailView(View):
    template_name = 'stats/stats_detail.html'

    def get(self, request, *args, id):
        model = get_object_or_404(ReceiveMoney, clId=id)
        return render(request, self.template_name, {'model': model.to_dict(model.shopName)})


def get_all_stats(request):
    ''' 获取所有门店结算数据 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    shopNo = request.GET.get('shopNo')
    payTime = request.GET.get('payTime')

    stats = ReceiveMoney.objects.filter(payType=2).extra(where=['status & 2=2'])
    if shopNo:
        stats = stats.filter(shopNo=shopNo)
    payTime = datetime.strptime(payTime, '%Y-%m') if payTime else datetime.now()

    stats = stats.filter(payTime__year=payTime.year, payTime__month=payTime.month) \
        .values('shopNo') \
        .annotate(totalAmount=Sum('money'))  # G币消费、已支付 数据

    count = stats.count()  # 总数
    stats = stats[(page - 1) * pagesize:page * pagesize]

    shopNo_list = [item['shopNo'] for item in stats]
    shops = Shop.objects.filter(fiveSysId__in=shopNo_list).values('fiveSysId', 'shopName')

    result = []
    for item in stats:
        shopName = safe_dict_value(list(filter(lambda m: m['fiveSysId'] == item['shopNo'], shops)), 'shopName')
        result.append({'shopNo': item['shopNo'],
                       'shopName': shopName,
                       'totalAmount': item['totalAmount']
                       })

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


class StatsShopView(PermissionRequiredMixin, View):
    template_name = 'stats/stats_shop.html'
    permission_required = ('shop.view_shop')

    def get(self, request, *args, **kwargs):
        shopNo = request.GET.get('shopNo')
        payTime = request.GET.get('payTime')  # 查询年月
        # context = User.objects.get_id_name(userId)
        return render(request, self.template_name, {'shopNo': shopNo, 'payTime': payTime})


def get_shop_stats(request):
    ''' 获取门店结算数据 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    shopNo = request.GET.get('shopNo')
    payTime = request.GET.get('payTime')

    stats = ReceiveMoney.objects.filter(payType=2).extra(where=['status & 2=2'])
    if shopNo:
        stats = stats.filter(shopNo=shopNo)
    payTime = datetime.strptime(payTime, '%Y-%m') if payTime else datetime.now()

    stats = stats.filter(payTime__year=payTime.year, payTime__month=payTime.month)

    count = stats.count()  # 总数
    stats = stats[(page - 1) * pagesize:page * pagesize]

    shopNo_list = [item.shopNo for item in stats]
    shops = Shop.objects.filter(fiveSysId__in=shopNo_list).values('fiveSysId', 'shopName')

    result = []
    for item in stats:
        shopName = safe_dict_value(list(filter(lambda m: m['fiveSysId'] == item.shopNo, shops)), 'shopName')
        result.append(item.to_dict(shopName))

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
