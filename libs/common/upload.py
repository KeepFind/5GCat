# coding:utf-8
from datetime import datetime

import qiniu
from django.conf import settings


def qiniu_upload(file, file_dir):
    now = datetime.now()
    # 上传文件名称
    file_name = '{dir}/{year}/{month}/{day}/{name}'.format(dir=file_dir, year=now.year, month=now.month, day=now.day,
                                                           name=file.name)
    url = '/' + file_name

    try:
        q = qiniu.Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        token = q.upload_token(settings.QINIU_BUCKET)

        ret, info = qiniu.put_stream(token, file_name, file, file_name, file.size)
        if not ret or not ret['hash']:
            return False, ''
    except Exception as e:
        return False, ''

    return True, url

