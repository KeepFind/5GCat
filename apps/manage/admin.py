from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from . import models


class AuthUserAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super(AuthUserAdmin, self).__init__(*args, **kwargs)
        self.list_display = ('username', 'email', 'is_active', 'is_staff', 'is_superuser')
        self.search_fields = ('username', 'email')

    def changelist_view(self, request, extra_context=None):
        # 这个方法在源码的admin/options.py文件的ModelAdmin这个类中定义，我们要重新定义它，以达到不同权限的用户，返回的表单内容不同

        self.fieldsets = ((None, {'fields': ('username', 'password',)}),
                          (_('Personal info'),
                           {'fields': ('realName', 'mobile', 'email')}),
                          (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
                          (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
                          )
        self.add_fieldsets = ((None, {'classes': ('wide',),
                                      'fields': (
                                          'username', 'mobile', 'password1', 'password2', 'realName', 'email',
                                          'is_active',
                                          'is_staff', 'is_superuser', 'groups'),
                                      }),
                              )

        return super(AuthUserAdmin, self).changelist_view(request, extra_context)


admin.site.register(models.AuthUser, AuthUserAdmin)
