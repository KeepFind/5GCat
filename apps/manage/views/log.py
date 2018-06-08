from django.contrib.admin.models import LogEntry
from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from common.response import paged_result
from common.string_extension import formattime, safe_dict_value, cast_endtime
from manage.models import ACTION_FLAG, AuthUser


class LogView(PermissionRequiredMixin, View):
    template_name = 'manage/log.html'
    permission_required = ('manage.view_logentry')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


def get_logs(request):
    ''' 获取日志列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    # raId = request.GET.get('raId')
    actionStart = request.GET.get('actionStart')
    actionEnd = request.GET.get('actionEnd')

    logs = LogEntry.objects.all()
    if actionStart:
        logs = logs.filter(action_time__gte=actionStart)
    if actionEnd:
        logs = logs.filter(action_time__lt=cast_endtime(actionEnd))

    count = logs.count()  # 总数
    logs = logs.order_by('-action_time')[(page - 1) * pagesize:page * pagesize]

    user_ids = list(logs.values_list('user_id', flat=True))
    users = AuthUser.objects.filter(id__in=user_ids).values('id', 'username')

    result = [{'id': item.id,
               'object_id': item.object_id,
               'object_repr': item.object_repr,
               'action_flag': ACTION_FLAG.get(item.action_flag),
               'ip': item.change_message,
               'user_id': item.user_id,
               'username': safe_dict_value(list(filter(lambda m: m['id'] == item.user_id, users)), 'username'),
               'action_time': formattime(item.action_time)
               } for item in logs]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
