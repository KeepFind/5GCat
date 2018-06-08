# coding:utf-8
import os
from datetime import datetime

from django import forms

from ad.models import Adposition, Advertisement
from common.form import check_image_extensions, save_image


class AdEditForm(forms.ModelForm):
    posiId = forms.IntegerField()
    title = forms.CharField(required=False, max_length=80)
    image = forms.ImageField(required=False, validators=[check_image_extensions])
    imageurl = forms.CharField(required=False)

    class Meta:
        model = Advertisement
        exclude = ['adId', 'adPosition', 'adType', 'status', 'createdTime', 'createdUser', 'updatedTime', 'updatedUser']

    def __init__(self, *args, **kwargs):
        if args:
            self.ad_type = args[0].get('ad_type')
        instance = kwargs.get('instance')
        if instance:
            kwargs['initial'] = {'posiId': instance.adPosition.posiId}

            self.posiName = instance.adPosition.posiName
            self.ad_type = 'article' if instance.adType == 2  else 'img'

        super(AdEditForm, self).__init__(*args, **kwargs)
        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

    def clean_posiId(self):
        self.adPosition = Adposition.objects.get(posiId=self.cleaned_data.get('posiId'))
        self.posiName = self.adPosition.posiName
        return self.cleaned_data.get('posiId')

    def clean_title(self):
        if self.ad_type == 'article':
            if not self.cleaned_data.get('title'):
                raise forms.ValidationError('标题不能为空')
        return self.cleaned_data.get('title')

    def clean(self):
        if self.ad_type == 'article':
            content = self.cleaned_data.get('adContents')
            linkUrl = self.cleaned_data.get('linkUrl')

            if not content and not linkUrl:
                raise forms.ValidationError({'adContents': '内容与链接不能同时为空'})
        else:
            image = self.cleaned_data.get('image')
            imageurl = self.cleaned_data.get('imageurl')
            if not image and not imageurl:
                raise forms.ValidationError({'image': '图片不能为空'})

            is_success, url = save_image(image, imageurl)
            if not is_success:
                raise forms.ValidationError({'image': '图片上传失败'})
            self.imageurl = url

    def save(self, commit=True):
        model = super(AdEditForm, self).save(False)
        if not model.createdTime:
            model.createdTime = datetime.now()
        model.updatedTime = datetime.now()

        model.adPosition = self.adPosition
        model.adType = 2 if self.ad_type == 'article' else 1
        if self.ad_type != 'article':
            model.title = self.imageurl

        return model



class AdPositionEditForm(forms.ModelForm):
    class Meta:
        model = Adposition
        exclude = ['posiId', 'status', 'createdTime', 'createdUser', 'updatedTime', 'updatedUser']

    def __init__(self, *args, **kwargs):
        super(AdPositionEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        model = super(AdPositionEditForm, self).save(False)
        if not model.createdTime:
            model.createdTime = datetime.now()
        model.updatedTime = datetime.now()

        return model
