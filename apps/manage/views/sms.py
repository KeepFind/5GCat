from django.shortcuts import render

# Create your views here.

import json
from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from activity.forms import ActivityEditForm
from activity.models import RidersActivity
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from manage.models import SmsRecord


class SmsView(PermissionRequiredMixin, View):
    template_name = 'manage/sms.html'
    permission_required = ('manage.view_smsrecord')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SmsDetailView(View):
    template_name = 'manage/sms_detail.html'

    def get(self, request, *args, id):
        model = get_object_or_404(SmsRecord, srId=id)
        return render(request, self.template_name, {'model': model.to_dict()})


def get_sms(request):
    ''' 获取短信列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    raId = request.GET.get('raId')
    acStart = request.GET.get('acStart')
    acEnd = request.GET.get('acEnd')

    sms = SmsRecord.objects.all()

    count = sms.count()  # 总数
    sms = sms.order_by('-sendTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in sms]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
