# coding:utf-8
from datetime import datetime

from django import forms

from account.models import PayInfo
from common.form import attrs

ACTIVATE_CHOICE = (
    (0, '启用'),
    (1, '停用')
)


class ProductForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), max_length=255, required=False)
    activate_status = forms.ChoiceField(choices=ACTIVATE_CHOICE)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            kwargs['initial'] = {
                'activate_status': (instance.status & 2) >> 1,
            }

        super(ProductForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

    class Meta:
        model = PayInfo
        exclude = ['piId', 'createdTime', 'createdUser', 'updatedTime', 'updatedUser', 'status']

    def save(self, commit=True):
        model = super(ProductForm, self).save(False)
        if not model.createdTime:
            model.createdTime = datetime.now()
        model.updatedTime = datetime.now()

        return model
