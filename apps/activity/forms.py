# coding:utf-8
from datetime import datetime

from django import forms

from activity.models import RidersActivity
from common.form import attrs


class ActivityEditForm(forms.ModelForm):
    class Meta:
        model = RidersActivity
        exclude = ['raId', 'status', 'createdTime', 'createdUser', 'updatedTime', 'updatedUser']

    def __init__(self, *args, **kwargs):
        super(ActivityEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            if name == 'signflag':
                self.fields[name].widget.attrs['class'] = 'cbox checkbox'
            else:
                self.fields[name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        model = super(ActivityEditForm, self).save(False)
        if not model.createdTime:
            model.createdTime = datetime.now()
        model.updatedTime = datetime.now()

        return model
