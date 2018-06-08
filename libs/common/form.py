# coding:utf-8
import os

from django.forms import ValidationError

from common.upload import qiniu_upload

attrs = {
    'class': 'form-control',
}

invalid_msg = '<span class="field-validation-error" data-valmsg-replace="true">' \
              '<span>{0}</span>' \
              '</span>'

login_invalid_msg = '<span class="Validform_checktip Validform_wrong">{0}</span>'


def save_image(image_file, old_image_filename):
    if image_file and not isinstance(image_file, str):
        is_success, url = qiniu_upload(image_file, 'ad')
        return is_success, url  # 上传图片
    if not old_image_filename:  # 删除图片
        return True, ''
    return True, old_image_filename  # 无修改


def check_image_extensions(value):
    '''图片格式校验'''
    if value and value.name:
        if os.path.splitext(value.name)[1] not in ['.jpg', '.png', '.bmp']:
            raise ValidationError('图片格式错误')
