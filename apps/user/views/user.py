import json
from datetime import datetime, timedelta

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from common.string_extension import cast_endtime
from manage.signals import post_logic_delete
from shop.models import Shop
from user.forms import UserEditForm
from user.models import User, UserInfo


class UserView(PermissionRequiredMixin, View):
    template_name = 'user/user.html'
    permission_required = ('user.view_user')

    def get(self, request, *args, **kwargs):
        userId = request.GET.get('userId')
        context = User.objects.get_id_name(userId)
        return render(request, self.template_name, context)


class UserEditView(PermissionRequiredMixin, View):
    template_name = 'user/user_edit.html'
    permission_required = ('user.change_user')

    def get(self, request, *args, id):
        user = get_object_or_404(UserInfo, user_id=id)
        form = UserEditForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        user = get_object_or_404(UserInfo, user_id=id)
        form = UserEditForm(request.POST, instance=user)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        user = form.save(commit=False)
        user.updatedUser = request.user.username
        user.updatedTime = datetime.now()
        user.save()

        return redirect('user:user')


class UserDetailView(View):
    template_name = 'user/user_detail.html'

    def get(self, request, *args, id):
        user = get_object_or_404(User, userId=id)
        return render(request, self.template_name, {'model': user})


def get_users(request):
    ''' 获取用户列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    userId = request.GET.get('userId')
    registerStart = request.GET.get('registerStart')
    registerEnd = request.GET.get('registerEnd')

    users = User.objects.extra(where=['status & 4=0'])  # 非删除、非店长
    if userId:
        users = users.filter(userId=userId)
    if registerStart:
        users = users.filter(registerTime__gte=registerStart)
    if registerEnd:
        users = users.filter(registerTime__lt=cast_endtime(registerEnd))

    count = users.count()  # 总数
    users = users.order_by('-registerTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in users]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


@csrf_exempt
@permission_required2('user.change_user')
@require_http_methods(['POST'])
def set_status(request):
    try:
        id = request.POST.get('id')
        opt = request.POST.get('opt')
        flag = int(request.POST.get('flag'))
        if int(flag) not in [0, 1]: raise

        # opt  ['activate', 'shop']
        user = User.objects.get(userId=id)
        if opt == 'activate':  # 激活
            user.status = (user.status & 4) + (flag << 1) + (user.status & 1)
        if opt == 'shop':  # 设置、取消店长
            user.status = (flag << 2) + (user.status & 2) + (user.status & 1)

        user.updatedUser = request.user.username
        user.save()

        return JSONResponse(success=True)
    except:
        return JSONResponse(success=False)


@csrf_exempt
@permission_required2('user.delete_user')
@require_http_methods(['POST'])
def delete_user(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        User.objects.filter(userId__in=ids).update(status=F('status').bitand(4) + F('status').bitand(2) + 1)
        post_logic_delete.send(sender='delete_user', app_label='user', model_name='user', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()


def selector_users(request):
    '''用户选择下拉框'''
    userName = request.GET.get('userName', '')
    if len(userName) < 3:
        return JsonResponse({'value': []}, safe=False)

    users = User.objects.filter(userName__contains=userName).values('userId', 'userName')
    results = {'value': [{'userId': item['userId'], 'userName': item['userName']} for item in users]}

    return JsonResponse(results, safe=False)
