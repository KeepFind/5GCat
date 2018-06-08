# coding:utf-8
from datetime import datetime

from django import forms
from django.db.models import F
from django.conf import settings

from article.models import Headline
from common.form import check_image_extensions, save_image


class HeadlineEditForm(forms.ModelForm):
    is_top = forms.BooleanField(required=False)
    imgUrl = forms.ImageField(required=False, validators=[check_image_extensions])
    imgUrlurl = forms.CharField(required=False)

    class Meta:
        model = Headline
        exclude = ['headlineId', 'status', 'thumbnailUrl', 'createdTime', 'createdUser', 'updatedTime', 'updatedUser']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            kwargs['initial'] = {'is_top': (instance.status & 2) == 2}

        super(HeadlineEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            if name == 'is_top':
                self.fields[name].widget.attrs['class'] = 'cbox checkbox'
            else:
                self.fields[name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        data = self.cleaned_data
        img_file = data.get('imgUrl')
        imgUrl_str = data.get('imgUrlurl')

        model = super(HeadlineEditForm, self).save(False)
        if not model.createdTime:
            model.createdTime = datetime.now()
        model.updatedTime = datetime.now()

        is_success, url = save_image(img_file, imgUrl_str)
        model.imgUrl = url
        model.thumbnailUrl = url + '?' + settings.HEADLINE_THUMB

        is_top = data.get('is_top')
        if is_top:  # 取消已置顶的头条
            Headline.objects.extra(where=['status & 2 = 2']).update(status=F('status').bitand(1))

        return model
