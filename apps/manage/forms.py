from django import forms
from django.contrib import auth
from django.contrib.auth.models import Group, Permission

from common.form import attrs
from manage.models import AuthUser


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '用户名', 'autofocus': ''}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': '密码'}))

    def __init__(self, *args, **kwargs):
        self.user = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        users = AuthUser.objects.filter(username=username)
        if not users:
            raise forms.ValidationError({'username': '用户不存在'})
        if not users[0].is_active:
            raise forms.ValidationError({'username': '用户未激活'})

        self.user = auth.authenticate(username=username, password=password)
        if not self.user:
            raise forms.ValidationError({'username': '用户名或密码错误'})


class UserAddForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs=attrs), max_length=20)
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs))

    class Meta:
        model = AuthUser
        fields = ['username', 'password']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError('两次密码不一致')
        return password2


GENDER_OPTIONS = (
    (1, '男'),
    (0, '女'),
)


class UserEditForm(forms.ModelForm):
    mobile = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    gender = forms.ChoiceField(widget=forms.Select(), choices=GENDER_OPTIONS)

    class Meta:
        model = AuthUser
        fields = ['mobile', 'email', 'gender', 'realname']

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            self.username = kwargs.get('instance').username

        super(UserEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'


def permission_all():
    # 全部权限
    return Permission.objects.all().values_list('id', 'name')


class UserPermForm(forms.ModelForm):
    select_attrs = {
        'class': 'form-control',
        'size': 15,
        'multiple': 'multiple'
    }

    username = forms.CharField(widget=forms.TextInput(attrs=attrs))
    groups_all = forms.CharField(widget=forms.Select(attrs=select_attrs), required=False)
    groups = forms.CharField(widget=forms.SelectMultiple(attrs=select_attrs), required=False)

    permissions_all = forms.CharField(widget=forms.Select(attrs=select_attrs), required=False)
    permissions = forms.CharField(widget=forms.SelectMultiple(attrs=select_attrs), required=False)

    def __init__(self, *args, **kwargs):
        super(UserPermForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['readonly'] = 'true'

        perm_widget = self.fields['permissions'].widget
        group_widget = self.fields['groups'].widget
        permall_widget = self.fields['permissions_all'].widget
        groupall_widget = self.fields['groups_all'].widget

        if kwargs['instance']:
            user = kwargs.get('instance')
            # 已拥有角色
            group_widget.choices = user.groups.values_list('id', 'name')
            # 已拥有权限
            perm_widget.choices = user.user_permissions.values_list('id', 'name')

        permall_widget.choices = permission_all()  # 所有权限
        groupall_widget.choices = Group.objects.all().values_list('id', 'name')  # 所有角色

        groupall_widget.attrs['class'] = 'js-multiselect1 form-control'
        permall_widget.attrs['class'] = 'js-multiselect2 form-control'

        group_widget.attrs['id'] = 'js_multiselect_to_1'
        perm_widget.attrs['id'] = 'js_multiselect_to_2'

    class Meta:
        model = AuthUser
        fields = ['username']


class UserResetPwdForm(forms.ModelForm):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(UserResetPwdForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            if name == 'username':
                self.fields[name].widget.attrs['readonly'] = 'true'
            self.fields[name].widget.attrs['class'] = 'form-control'

    class Meta:
        model = AuthUser
        fields = ['username', 'password']

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError('两次密码不一致')
        return password2


class GroupForm(forms.ModelForm):
    select_attrs = {
        'class': 'js-multiselect form-control',
        'size': 15,
        'multiple': 'multiple'
    }

    select_attrs2 = {'id': 'js_multiselect_to_1',
                     'class': 'form-control',
                     'size': 15,
                     'multiple': 'multiple'
                     }

    name = forms.CharField(widget=forms.TextInput(attrs=attrs))
    permissions_all = forms.CharField(widget=forms.Select(attrs=select_attrs), required=False)
    permissions = forms.CharField(widget=forms.SelectMultiple(attrs=select_attrs2), required=False)

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        group = kwargs.get('instance')
        if group:
            # 已有权限
            self.fields['permissions'].widget.choices = group.permissions.values('id', 'name')
        # 全部权限
        self.fields['permissions_all'].widget.choices = permission_all()

    class Meta:
        model = Group
        fields = ['name']


AWARD_LEVEL = (
    (1, '一级'),
    (2, '二级'),
    (3, '三级'),
)


class ConfigEditForm(forms.Form):
    REWARD_LEVEL = forms.ChoiceField(choices=AWARD_LEVEL)
    FIRST_AWARD = forms.FloatField(required=False)
    SECOND_AWARD = forms.FloatField(required=False)
    THREE_AWARD = forms.FloatField(required=False)

    WITHDRAW_RATE = forms.FloatField(required=False)
    WITHDRAW_HOW_DAYS = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        configs = kwargs.get('initial')  # [{('configKey','configVallue')]
        if configs:
            initial = {}
            for configKey, configValue in configs:
                initial[configKey] = configValue
            kwargs['initial'] = initial

        super(ConfigEditForm, self).__init__(*args, **kwargs)

        for name, _ in self.fields.items():
            self.fields[name].widget.attrs['class'] = 'form-control'
