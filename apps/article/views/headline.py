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

from article.forms import HeadlineEditForm
from article.models import Headline
from common.decorators import permission_required2
from common.form import invalid_msg
from common.http import JSONResponse
from common.response import paged_result
from manage.signals import post_logic_delete


class HeadlineView(PermissionRequiredMixin, View):
    template_name = 'article/headline.html'
    permission_required = ('article.view_headline')

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class HeadlineAddView(PermissionRequiredMixin, View):
    template_name = 'article/headline_add.html'
    permission_required = ('article.add_headline')

    def get(self, request, *args, **kwargs):
        form = HeadlineEditForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = HeadlineEditForm(request.POST, request.FILES)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        model.updatedUser = request.user.username
        model.status = 2 if form.cleaned_data.get('is_top') else 0
        model.save()

        return redirect('article:headline')


class HeadlineEditView(PermissionRequiredMixin, View):
    template_name = 'article/headline_edit.html'
    permission_required = ('article.change_headline')

    def get(self, request, *args, id):
        headline = get_object_or_404(Headline, headlineId=id)
        form = HeadlineEditForm(instance=headline)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, id):
        headline = get_object_or_404(Headline, headlineId=id)
        form = HeadlineEditForm(request.POST, request.FILES, instance=headline)
        if not form.is_valid():
            errors = {key: invalid_msg.format(value[0]) for key, value in form.errors.items()}
            return render(request, self.template_name, {'error': errors, 'form': form})

        model = form.save(commit=False)
        value = 2 if form.cleaned_data.get('is_top') else 0
        model.updatedUser = request.user.username
        model.status = value + (model.status & 1)
        model.save()

        return redirect('article:headline')


def get_headlines(request):
    ''' 获取头条列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))

    headlines = Headline.objects.all()

    count = headlines.count()  # 总数
    headlines = headlines.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in headlines]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


@csrf_exempt
@permission_required2('article.change_headline')
@require_http_methods(['POST'])
def set_status(request):
    try:
        id = request.POST.get('id')
        opt = request.POST.get('opt')
        flag = int(request.POST.get('flag'))
        # if int(flag) not in [0, 1]: raise

        # opt  ['top']
        headline = Headline.objects.get(headlineId=id)
        if opt == 'top':  # 置顶
            Headline.objects.extra(where=['status & 2 = 2']).update(status=F('status').bitand(1))
            headline.status = 2 + (headline.status & 1)
            headline.updatedUser = request.user.username
            headline.save()

        return JSONResponse(success=True)
    except:
        return JSONResponse(success=False)


@csrf_exempt
@permission_required2('article.delete_headline')
@require_http_methods(['POST'])
def delete_headline(request):
    try:
        data = json.loads(request.body.decode())
        ids = data.get('ids')

        Headline.objects.filter(headlineId__in=ids).update(status=F('status').bitand(2) + 1,
                                                           updatedUser=request.user.username)
        post_logic_delete.send(sender='delete_headline', app_label='article', model_name='headline', ids=ids,
                               update_user_id=request.user.id)

    except Exception as e:
        return JSONResponse(msg='删除失败！', success=False)
    return JSONResponse()
