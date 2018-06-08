# coding:utf-8
from django import forms
from common.form import attrs
from manage.forms import GENDER_OPTIONS
from shop.models import Shop
from user.models import UserInfo


class UserAddForm(forms.ModelForm):
    userName = forms.CharField()
    gender = forms.ChoiceField(choices=GENDER_OPTIONS)

    class Meta:
        model = UserInfo
        exclude = ['infoId', 'user', 'payPwd', 'status']

    def __init__(self, *args, **kwargs):
        userInfo = kwargs.get('instance')
        if userInfo:
            kwargs['initial'] = {
                'userName': userInfo.user.userName,
            }

        super(UserAddForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

            if name == 'referralUserName':
                self.fields[name].widget.attrs['readonly'] = 'true'


class UserEditForm(forms.ModelForm):
    userName = forms.CharField()
    referralUserName = forms.CharField(required=False)
    gender = forms.ChoiceField(choices=GENDER_OPTIONS)

    class Meta:
        model = UserInfo
        exclude = ['infoId', 'user', 'payPwd', 'referralUser', 'status']

        # all_fields = model._meta.get_fields()
        # attrs = {item.name: attrs for item in all_fields if hasattr(item, 'name')}

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            referralUserName = instance.referralUser.userName if instance.referralUser else ''
            kwargs['initial'] = {
                'userName': instance.user.userName,
                'referralUserName': referralUserName
            }
            shop = Shop.objects.get_id_name(instance.defaultShopId) if instance.defaultShopId else None
            self.shopName = shop.get('shopName') if shop else ''

        super(UserEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

            if name == 'userName' or name == 'referralUserName':
                self.fields[name].widget.attrs['readonly'] = 'true'
