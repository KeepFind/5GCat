import json
import os
from datetime import datetime

from PIL import Image
from django.http import HttpResponse, JsonResponse
from django.conf import settings

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
import qiniu

from upload.models import Carbrand


@csrf_exempt
def ueditor(request):
    action = request.GET.get('action')
    if action == 'config':
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ueditor.json')
        with open(config_file, 'r', encoding='utf-8') as f:
            config = f.read()
            return HttpResponse(config, 'application/json')

    elif action == 'uploadimage':  # 上传图片
        file = request.FILES.get('file')
        now = datetime.now()
        # 上传文件名称
        file_name = 'article/{year}/{month}/{day}/{name}'.format(year=now.year, month=now.month, day=now.day,
                                                                 name=file.name)
        result = {
            'state': 'SUCCESS',
            'url': settings.QINIU_DOMAIN + '/' + file_name,
            'title': file.name,
            'original': file.name,
            'type': file.content_type,
            'size': file.size,
        }

        try:
            q = qiniu.Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
            token = q.upload_token(settings.QINIU_BUCKET)

            res, info = qiniu.put_stream(token, file_name, file, 'test', file.size)
            if not res:
                result['state'] = '上传失败！'
        except Exception as e:
            result['state'] = e
        return JsonResponse(result)
    else:
        return HttpResponse('success')


@csrf_exempt
def save_image(request):
    files = request.FILES.getlist('image')
    result = {'success': True}
    return JsonResponse(result)


def upload(request):
    q = qiniu.Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    token = q.upload_token('brandicon')

    import requests, sys, io
    brand_icons = list(Carbrand.objects.filter(brandicon__isnull=False).values_list('brandicon', flat=True))
    print(len(brand_icons))
    i = 0
    for item in brand_icons:
        print('开始抓取第{0}条'.format(i))
        result = requests.get('http://easy.jy-epc.com/icons/brand_icons/' + item)

        file = io.BytesIO(result.content)

        res, info = qiniu.put_stream(token, item, file, 'test', len(result.content))
        print(res, info)
        if not res:
            print('上传失败！')
        i = i + 1

    return HttpResponse('success')


    # res, info = qiniu.put_stream(token, file_name, file, 'test', file.size)
    # if not res:
    #     result['state'] = '上传失败！'
