import json

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission, Group
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
from manage.forms import UserPermForm, UserAddForm, UserEditForm, UserResetPwdForm
from manage.models import AuthUser
from manage.signals import post_logic_delete


class UserView(PermissionRequiredMixin, View):
    template_name = 'manage/user.html'
    permission_required = ('manage.view_user')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class UserAddView(PermissionRequiredMixin, View):
    template_name = 'manage/user_add.html'
    permission_required = ('manage.add_user')

    def get(self, request, *args, **kwargs):
        form = UserAddForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserAddForm(request.POST)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data.get('password'))
        user.is_staff = True
        user.is_active = True
        user.save()

        return redirect('manage:user')


class UserEditView(PermissionRequiredMixin, View):
    template_name = 'manage/user_edit.html'
    permission_required = ('manage.change_user')

    def get(self, request, *args, id):
        user = get_object_or_404(AuthUser, id=id)
        form = UserEditForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        user = get_object_or_404(AuthUser, id=id)
        form = UserEditForm(request.POST, instance=user)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        user = form.save(commit=False)
        user.is_staff = True
        # user.is_active = True
        user.save()

        return redirect('manage:user')


def get_users(request):
    ''' 获取管理用户列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    keyword = request.GET.get('keywords')

    users = AuthUser.objects.all()
    if keyword:
        users = users.filter(username__contains=keyword)  # 按名称查询
    count = users.count()  # 总数
    users = users.order_by('-date_joined')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in users]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


class UserPermView(PermissionRequiredMixin, View):
    '''用户授权'''
    template_name = 'manage/user_perm.html'
    permission_required = ('manage.change_userperm')

    def get(self, request, *args, id):
        user = get_object_or_404(AuthUser, id=id)
        form = UserPermForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        user = get_object_or_404(AuthUser, id=id)
        form = UserPermForm(request.POST, instance=user)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        group_ids = request.POST.getlist('groups', [])
        groups = Group.objects.filter(id__in=[int(item) for item in group_ids])

        permission_ids = request.POST.getlist('permissions', [])
        permissions = Permission.objects.filter(id__in=[int(item) for item in permission_ids])

        user = form.save(commit=False)
        user.groups = groups
        user.user_permissions = permissions  # 保存权限
        user.save()

        return redirect('manage:user')


class UserResetPwdView(View):
    '''重置密码'''
    template_name = 'manage/user_resetpwd.html'

    def get(self, request, *args, **kwargs):
        user = get_object_or_404(AuthUser, id=request.user.id)
        form = UserResetPwdForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(AuthUser, id=request.user.id)
        form = UserResetPwdForm(request.POST, instance=user)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        user = form.save(commit=False)
        user.password = make_password(form.cleaned_data.get('password'))
        user.save()

        return redirect('manage:user')


@csrf_exempt
@permission_required2('authuser.change_user')
@require_http_methods(['POST'])
def set_status(request):
    try:
        id = request.POST.get('id')
        opt = request.POST.get('opt')
        flag = int(request.POST.get('flag'))
        if int(flag) not in [0, 1]: raise

        # opt  ['activate', 'shop']
        user = AuthUser.objects.get(id=id)
        if opt == 'activate':  # 激活
            user.is_active = True if flag == 1 else False
        user.updatedUser = request.user.username
        user.save()

        return JSONResponse(success=True)
    except:
        return JSONResponse(success=False)


@csrf_exempt
@permission_required2('manage.delete_user')
@require_http_methods(['POST'])
def delete_user(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        with transaction.atomic():
            users = AuthUser.objects.filter(id__in=ids)
            # 删除关联角色、权限
            for item in users:
                item.groups.all().delete()
                item.user_permissions.all().delete()
            # 删除用户
            users.delete()

        post_logic_delete.send(sender='delete_user', app_label='manage', model_name='authuser', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！')
    return JSONResponse()
