import json
from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from activity.models import ActivitySign
from common.response import paged_result
from common.string_extension import cast_endtime


class SignView(PermissionRequiredMixin, View):
    template_name = 'activity/sign.html'
    permission_required = ('activity.view_activitysign')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


def get_signs(request):
    ''' 获取活动报名列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    raId = request.GET.get('raId')
    createStart = request.GET.get('createStart')
    createEnd = request.GET.get('createEnd')

    signs = ActivitySign.objects.select_related().all()
    if raId:
        signs = signs.filter(ridersActivity__raId=raId)
    if createStart:
        signs = signs.filter(createdTime__gte=createStart)
    if createEnd:
        signs = signs.filter(createdTime__lt=cast_endtime(createEnd))

    count = signs.count()  # 总数
    signs = signs.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in signs]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
