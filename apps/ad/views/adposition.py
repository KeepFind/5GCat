import json
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
from manage.signals import post_logic_delete


class AdPositionView(PermissionRequiredMixin, View):
    template_name = 'ad/adposition.html'
    permission_required = ('ad.view_adposition')

    def get(self, request, *args, **kwargs):
        posiId = request.GET.get('posiId')
        context = Adposition.objects.get_id_name(posiId)
        return render(request, self.template_name, context)


class AdPositionAddView(PermissionRequiredMixin, View):
    template_name = 'ad/adposition_add.html'
    permission_required = ('ad.add_adposition')

    def get(self, request, *args, **kwargs):
        form = AdPositionEditForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AdPositionEditForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.save()

        return redirect('activity:activity')


def get_adpositions(request):
    ''' 获取广告位列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))

    adpositions = Adposition.objects.all()

    count = adpositions.count()  # 总数
    adpositions = adpositions.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in adpositions]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


@csrf_exempt
@permission_required2('ad.change_adposition')
@require_http_methods(['POST'])
def set_status(request):
    try:
        id = request.POST.get('id')
        opt = request.POST.get('opt')
        flag = int(request.POST.get('flag'))
        if int(flag) not in [0, 1]: raise

        # opt  ['activate']
        adposition = Adposition.objects.get(posiId=id)

        if opt == 'activate':  # 激活
            adposition.status = (flag << 1) + (adposition.status & 1)
            adposition.updatedUser = request.user.username
            adposition.save()

        return JSONResponse(success=True)
    except:
        return JSONResponse(success=False)


@csrf_exempt
@permission_required2('ad.delete_adposition')
@require_http_methods(['POST'])
def delete_adposition(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        Adposition.objects.filter(posiId__in=ids).update(status=F('status').bitand(2) + 1)
        post_logic_delete.send(sender='delete_adposition', app_label='ad', model_name='adposition', ids=ids,
                               update_user_id=request.user.id)


    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()


def selector_adpositions(request):
    '''广告位选择下拉框'''
    posiName = request.GET.get('posiName', '')

    adpositions = Adposition.objects.filter(posiName__contains=posiName).values('posiId', 'posiName')
    results = {'value': [{'posiId': item['posiId'], 'posiName': item['posiName']} for item in adpositions]}

    return JsonResponse(results, safe=False)
