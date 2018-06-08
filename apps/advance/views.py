# coding:utf-8
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from advance.models import AdvanceInfo
from common.response import paged_result
from common.string_extension import safe_dict_value
from shop.models import Shop
from user.models import User


class AdvanceView(PermissionRequiredMixin, View):
    '''预约管理'''
    template_name = 'advance/advance.html'
    permission_required = ('advance.view_advanceinfo')

    def get(self, request, *args, **kwargs):
        userId = request.GET.get('userId')
        context = User.objects.get_id_name(userId)
        return render(request, self.template_name, context)


class AdvanceDetailView(View):
    template_name = 'advance/advance_detail.html'

    def get(self, request, *args, id):
        model = get_object_or_404(AdvanceInfo, infoId=id)
        return render(request, self.template_name, {'model': model.to_dict(model.shopName)})


def get_advances(request):
    ''' 获取预约列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    userId = request.GET.get('userId')
    shopNo = request.GET.get('shopNo')

    advances = AdvanceInfo.objects.all()
    if userId:
        advances = advances.filter(user__userId=userId)
    if shopNo:
        advances = advances.filter(shopNo=shopNo)

    count = advances.count()  # 总数
    advances = advances.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    advances = list(advances)

    shopNo_list = [item.shopNo for item in advances]
    shops = Shop.objects.filter(fiveSysId__in=shopNo_list).values('fiveSysId', 'shopName')

    result = []
    for advance in advances:
        shopName = safe_dict_value(list(filter(lambda m: m['fiveSysId'] == advance.shopNo, shops)), 'shopName')
        result.append(advance.to_dict(shopName))

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
