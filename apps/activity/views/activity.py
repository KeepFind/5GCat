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

from activity.forms import ActivityEditForm
from activity.models import RidersActivity
from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from common.string_extension import cast_endtime
from manage.signals import post_logic_delete
from user.models import User


class ActivityView(PermissionRequiredMixin, View):
    template_name = 'activity/activity.html'
    permission_required = ('activity.view_ridersactivity')

    def get(self, request, *args, **kwargs):
        raId = request.GET.get('raId')
        context = RidersActivity.objects.get_id_name(raId)
        return render(request, self.template_name, context)


class ActivityAddView(PermissionRequiredMixin, View):
    template_name = 'activity/activity_add.html'
    permission_required = ('activity.add_ridersactivity')

    def get(self, request, *args, **kwargs):
        form = ActivityEditForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ActivityEditForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.createdUser = request.user.username
        model.updatedUser = request.user.username
        model.status = 0
        model.save()

        return redirect('activity:activity')


class ActivityEditView(PermissionRequiredMixin, View):
    template_name = 'activity/activity_edit.html'
    permission_required = ('activity.change_ridersactivity')

    def get(self, request, *args, id):
        activity = get_object_or_404(RidersActivity, raId=id)
        form = ActivityEditForm(instance=activity)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        activity = get_object_or_404(RidersActivity, raId=id)
        form = ActivityEditForm(request.POST, instance=activity)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.createdUser = request.user.username
        model.updatedUser = request.user.username
        model.save()

        return redirect('activity:activity')


def get_activities(request):
    ''' 获取活动列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    raId = request.GET.get('raId')
    acStart = request.GET.get('acStart')
    acEnd = request.GET.get('acEnd')

    acitivities = RidersActivity.objects.all()
    if raId:
        acitivities = acitivities.filter(raId=raId)
    if acStart:
        acitivities = acitivities.filter(acTime__gte=acStart)
    if acEnd:
        acitivities = acitivities.filter(acTime__lt=cast_endtime(acEnd))

    count = acitivities.count()  # 总数
    acitivities = acitivities.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in acitivities]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


@csrf_exempt
@permission_required2('activity.delete_ridersactivity')
@require_http_methods(['POST'])
def delete_activity(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        RidersActivity.objects.filter(raId__in=ids).update(status=1, updatedUser=request.user.username)
        post_logic_delete.send(sender='delete_activity', app_label='activity', model_name='ridersactivity', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()


def selector_activities(request):
    '''活动选择下拉框'''
    acTitle = request.GET.get('acTitle', '')
    if not acTitle:
        return JsonResponse({'value': []}, safe=False)

    activities = RidersActivity.objects.filter(acTitle__contains=acTitle).values('raId', 'acTitle')
    results = {'value': [{'raId': item['raId'], 'acTitle': item['acTitle']} for item in activities]}

    return JsonResponse(results, safe=False)
