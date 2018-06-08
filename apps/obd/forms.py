# coding:utf-8
import os
from datetime import datetime

from django import forms

from ad.models import Adposition, Advertisement
from common.form import check_image_extensions, save_image
from obd.models import ObdDevice


class ObdAddForm(forms.ModelForm):
    class Meta:
        model = ObdDevice
        exclude=()
        # exclude = ['sn', 'producerName', 'producerAddress', 'status', 'createdTime', 'createdUser', 'updatedTime', 'updatedUser']

    def __init__(self, *args, **kwargs):
        super(ObdAddForm, self).__init__(*args, **kwargs)
        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        model = super(ObdAddForm, self).save()
        return model
