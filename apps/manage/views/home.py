# coding:utf-8
from django.contrib import auth
from django.contrib.admin.models import LogEntry
from django.shortcuts import render, redirect
from django.views import View

from common.form import login_invalid_msg
from manage.forms import LoginForm


def index(request):
    '''后台首页'''
    return render(request, 'index.html')


def welcome(request):
    '''内容页 首页'''
    return render(request, 'welcome.html')


def unauthorized(request):
    '''401无权限页'''
    return render(request, '401.html')


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if not form.is_valid():
            errors = {key: login_invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        auth.login(request, form.user)

        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        # 登录日志
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=None,
            object_id=request.user.id,
            object_repr='登录',
            action_flag=4,
            change_message=ip,
        )

        return redirect('home')


def logout(request):
    '''注销登录'''
    # 登出日志
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=None,
        object_id=request.user.id,
        object_repr='登出',
        action_flag=5,
        change_message='',
    )
    auth.logout(request)
    return redirect('login')
