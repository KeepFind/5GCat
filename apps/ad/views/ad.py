import json
import os
from datetime import datetime

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ad.forms import AdPositionEditForm, AdEditForm
from ad.models import Adposition, Advertisement
from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from common.string_extension import cast_endtime
from common.upload import qiniu_upload
from manage.signals import post_logic_delete


class AdView(PermissionRequiredMixin, View):
    template_name = 'ad/ad.html'
    permission_required = ('ad.view_advertisement')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class AdAddView(PermissionRequiredMixin, View):
    template_name = 'ad/ad_add.html'
    permission_required = ('ad.add_advertisement')

    def get(self, request, *args, ad_type):
        form = AdEditForm()
        form.ad_type = ad_type
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AdEditForm(request.POST, request.FILES)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.createdUser = request.user.username
        model.updatedUser = request.user.username
        model.status = 0
        model.save()

        return redirect('ad:ad')


class AdEditView(PermissionRequiredMixin, View):
    template_name = 'ad/ad_edit.html'
    permission_required = ('ad.change_advertisement')

    def get(self, request, *args, id):
        ad = get_object_or_404(Advertisement, adId=id)
        form = AdEditForm(instance=ad)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        ad = get_object_or_404(Advertisement, adId=id)
        form = AdEditForm(request.POST, request.FILES, instance=ad)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.updatedUser = request.user.username
        model.save()

        return redirect('ad:ad')


def get_ads(request):
    ''' 获取广告列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    posiId = request.GET.get('posiId')
    createStart = request.GET.get('createStart')
    createEnd = request.GET.get('createEnd')

    ads = Advertisement.objects.all()
    if posiId:
        ads = ads.filter(adPosition__posiId=posiId)
    if createStart:
        ads = ads.filter(createdTime__gte=createStart)
    if createEnd:
        ads = ads.filter(createdTime__lt=cast_endtime(createEnd))

    count = ads.count()  # 总数
    adpositions = ads.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in adpositions]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())



@csrf_exempt
@permission_required2('ad.delete_advertisement')
@require_http_methods(['POST'])
def delete_ad(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        Advertisement.objects.filter(adId__in=ids).update(status=1, updatedUser=request.user.username)
        post_logic_delete.send(sender='delete_ad', app_label='ad', model_name='advertisement', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()
