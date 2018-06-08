# coding:utf-8
from datetime import datetime

from django import forms

from shop.models import Shop, AuthShopManager


class ShopEditForm(forms.ModelForm):
    shopId = forms.IntegerField(required=False)

    class Meta:
        model = Shop
        exclude = ['createdTime', 'createdUser', 'updatedTime', 'updatedUser', 'status']

    def __init__(self, *args, **kwargs):
        super(ShopEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        model = super(ShopEditForm, self).save(False)
        if not model.createdTime:
            model.createdTime = datetime.now()
        model.updatedTime = datetime.now()

        return model


class ShopManagerAddForm(forms.ModelForm):
    shopNo = forms.CharField(max_length=50)
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = AuthShopManager
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(ShopManagerAddForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError('两次密码不一致')
        return password2

    def clean_shopNo(self):
        self.shop = Shop.objects.get(fiveSysId=self.cleaned_data.get('shopNo'))
        self.shopName = self.shop.shopName
        return self.cleaned_data.get('shopNo')

    # def clean(self):
    #     shopId = self.cleaned_data.get('shopId')
    #     username = self.cleaned_data.get('username')
    #     if AuthShopManager.objects.filter(username=username, shop__shopId=shopId).count() > 0:
    #         raise forms.ValidationError({'username': '用户名已存在'})

    def save(self, commit=True):
        model = super(ShopManagerAddForm, self).save(False)
        if not model.date_joined:
            model.date_joined = datetime.now()
        model.shopNo = self.shop.fiveSysId
        return model
