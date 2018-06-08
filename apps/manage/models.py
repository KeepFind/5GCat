from django.contrib.auth.models import AbstractUser
from django.db import models

from common.string_extension import formattime


class AuthUser(AbstractUser):
    realname = models.CharField('真实姓名', max_length=20, null=True, blank=True)
    gender = models.NullBooleanField('性别', max_length=40, blank=True, null=True)
    mobile = models.CharField('手机', max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'auth_user'
        verbose_name = '管理用户'

        permissions = (
            ('view_user', '系统-用户-查看'),
            ('change_userperm', '系统-用户-授权'),
        )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'mobile': self.mobile,
            'is_superuser': self.is_superuser,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'date_joined': self.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }


class SmsRecord(models.Model):
    srId = models.AutoField(primary_key=True)
    mobile = models.CharField(max_length=20)
    contents = models.CharField(max_length=512)
    platformId = models.SmallIntegerField()
    success = models.NullBooleanField(blank=True, null=True)
    sendTime = models.DateTimeField()

    class Meta:
        db_table = 'smsRecord'
        managed = False
        verbose_name = '短信'

        permissions = (
            ('view_smsrecord', '系统-短信-查看'),
        )

    def to_dict(self):
        return {
            'id': self.srId,
            'mobile': self.mobile,
            'contents': self.contents,
            'platformId': self.platformId,
            'success': ord(self.success),
            'sendTime': formattime(self.sendTime),
        }


class SysConfig(models.Model):
    '''系统配置表'''
    configId = models.AutoField(primary_key=True)
    configKey = models.CharField(max_length=20)
    configValue = models.CharField(max_length=20)
    configDesc = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'sysConfig'
        managed = False
        verbose_name = '系统配置'

        permissions = (
            ('view_sysconfig', '系统-系统配置-查看'),
        )


ACTION_FLAG = {
    1: '新增',
    2: '修改',
    3: '删除',
    4: '登录',
    5: '登出'
}
