from datetime import datetime

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from common.form import invalid_msg
from common.http import JSONResponse
from manage.forms import ConfigEditForm
from manage.models import SysConfig


class ConfigView(PermissionRequiredMixin, View):
    template_name = 'manage/config.html'
    permission_required = ('manage.view_sysconfig')

    def get(self, request, *args, **kwargs):
        configs = SysConfig.objects.all().values_list('configKey', 'configValue')
        form = ConfigEditForm(initial=configs)
        return render(request, self.template_name, {'form': form})


class ConfigEditView(View):
    template_name = 'manage/config.html'
    permission_required = ('manage.change_sysconfig')

    def post(self, request, *args, **kwargs):
        if not request.user.has_perms(self.permission_required):
            return JSONResponse(success=False, msg='您无此操作权限！')

        form = ConfigEditForm(request.POST)
        if not form.is_valid():
            error = form.errors.values()[0]
            return JSONResponse(success=False, msg=error)

        data = form.cleaned_data
        configs = SysConfig.objects.all()
        config_names = ['REWARD_LEVEL', 'FIRST_AWARD', 'SECOND_AWARD', 'THREE_AWARD',
                        'WITHDRAW_HOW_DAYS',
                        'WITHDRAW_RATE']

        for item in config_names:
            config = single_config(configs, item)
            config.configKey = item
            config.configValue = data.get(item)
            config.status = 0
            config.createdTime = datetime.now() if not config.createdTime else config.createdTime
            config.createdUser = request.user.username if not config.createdUser else config.createdUser
            config.save()

        return JSONResponse()


def single_config(configs, config_name):
    result = list(filter(lambda m: m.configKey == config_name, configs))
    return result[0] if len(result) > 0 else SysConfig()
