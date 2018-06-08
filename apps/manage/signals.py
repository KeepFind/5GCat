# coding:utf-8
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.apps import apps
import django.dispatch

from account.models import WithdrawOrder, PayInfo
from activity.models import RidersActivity
from ad.models import Advertisement, Adposition
from article.models import Headline
from manage.models import AuthUser, SysConfig
from shop.models import Shop, ShopManager
from user.models import User, UserInfo

# 逻辑删除 signal
post_logic_delete = django.dispatch.Signal(providing_args=['instance', 'upadatedUser'])


@receiver(post_save, sender=WithdrawOrder)
@receiver(post_save, sender=PayInfo)
@receiver(post_save, sender=RidersActivity)
@receiver(post_save, sender=Advertisement)
@receiver(post_save, sender=Adposition)
@receiver(post_save, sender=Headline)
@receiver(post_save, sender=AuthUser)
@receiver(post_save, sender=Group)
@receiver(post_save, sender=SysConfig)
@receiver(post_save, sender=Shop)
@receiver(post_save, sender=ShopManager)
@receiver(post_save, sender=User)
@receiver(post_save, sender=UserInfo)
def model_post_save(sender, **kwargs):
    action_flag = ADDITION if kwargs.get('created') is True else CHANGE

    try:
        instance = kwargs['instance']
        username = getattr(instance, 'updatedUser', '')
        update_user_id = AuthUser.objects.get(username=username).id if username else 1
        verbose_name = instance._meta.verbose_name

        # app_name = instance._meta.app_label
        # model_name = instance._meta.model_name
        # model = apps.get_model(app_name, model_name)

        LogEntry.objects.log_action(
            user_id=update_user_id,
            content_type_id=get_content_type_for_model(instance).id,
            object_id=instance.pk,
            object_repr='新增 ' if action_flag == 1 else '修改 ' + verbose_name,
            action_flag=action_flag,
            change_message='',
        )
    except Exception as e:
        pass


@receiver(post_logic_delete)
def model_delete(sender, **kwargs):
    app_label = kwargs.get('app_label')
    model_name = kwargs.get('model_name')
    ids = kwargs.get('ids')
    update_user_id = kwargs.get('update_user_id')

    try:
        content_type_id = ContentType.objects.get(app_label=app_label, model=model_name).id
        verbose_name = apps.get_model(app_label, model_name)._meta.verbose_name

        for id in ids:
            LogEntry.objects.log_action(
                user_id=update_user_id,
                content_type_id=content_type_id,
                object_id=id,
                object_repr='删除 ' + verbose_name,
                action_flag=DELETION,
                change_message='',
            )
    except Exception as e:
        pass
