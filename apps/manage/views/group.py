# coding:utf-8
import json

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from manage.forms import GroupForm
from manage.models import AuthUser
from manage.signals import post_logic_delete


class GroupView(PermissionRequiredMixin, View):
    template_name = 'manage/group.html'
    permission_required = ('auth.view_group')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class GroupAddView(PermissionRequiredMixin, View):
    template_name = 'manage/group_add.html'
    permission_required = ('auth.add_group')

    def get(self, request, *args, **kwargs):
        form = GroupForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = GroupForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        permission_ids = request.POST.getlist('permissions', [])
        permissions = Permission.objects.filter(id__in=[int(item) for item in permission_ids])

        group = form.save(commit=False)
        group.save()
        group.permissions = permissions  # 保存权限
        group.save()

        return redirect('manage:group')


class GroupEditView(PermissionRequiredMixin, View):
    template_name = 'manage/group_edit.html'
    permission_required = ('auth.chagne_group')

    def get(self, request, *args, id):
        group = get_object_or_404(Group, id=id)
        form = GroupForm(instance=group)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        group = get_object_or_404(Group, id=id)
        form = GroupForm(request.POST, instance=group)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        permission_ids = request.POST.getlist('permissions', [])
        permissions = Permission.objects.filter(id__in=[int(item) for item in permission_ids])

        group = form.save(commit=False)
        group.permissions = permissions  # 保存权限
        group.save()

        return redirect('manage:group')


@csrf_exempt
@permission_required2('auth.delete_group')
@require_http_methods(['POST'])
def delete_group(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        with transaction.atomic():
            groups = Group.objects.filter(id__in=ids)
            users = AuthUser.objects.filter(groups=groups)
            # 删除关联角色权限
            for item in groups:
                item.permissions.all().delete()
            # 删除关联用户角色
            for item in users:
                item.groups.all().delete()
            # 删除角色
            groups.delete()

        post_logic_delete.send(sender='delete_group', app_label='auth', model_name='group', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！')
    return JSONResponse()


def get_groups(request):
    ''' 获取角色列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    keyword = request.GET.get('keywords')

    groups = Group.objects.all()
    if keyword:
        groups = groups.filter(name__contains=keyword)  # 按名称查询
    count = groups.count()  # 总数
    groups = groups[(page - 1) * pagesize:page * pagesize]
    result = [{'id': item.id, 'name': item.name} for item in groups]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
