from django.db import models

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime


class ActivityManager(BaseManager, models.Manager):
    def get_id_name(self, raId):
        if raId:
            result = self.filter(raId=raId).values('raId', 'acTitle')
            if result:
                result = result[0]
            return result
        return None


class RidersActivity(models.Model):
    '''车友活动'''
    raId = models.AutoField(primary_key=True)
    acTitle = models.CharField(max_length=20)
    acBody = models.TextField()
    acTime = models.DateTimeField()
    acAddress = models.CharField(max_length=30)
    totalNum = models.IntegerField(blank=True, null=True)
    signflag = models.BooleanField()
    signNum = models.IntegerField(blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    objects = ActivityManager()

    class Meta:
        db_table = 'ridersActivity'
        managed = False
        verbose_name = '活动'

        permissions = (
            ('view_ridersactivity', '活动-查看'),
        )

    def to_dict(self):
        return {
            'id': self.raId,
            'acTitle': self.acTitle,
            'acBody': self.acBody,
            'acTime': formattime(self.acTime),
            'acAddress': self.acAddress,
            'totalNum': self.totalNum,
            'signflag': ord(self.signflag),
            'signNum': self.signNum,
            'status': self.status,
            'createdTime': formattime(self.createdTime),
            'createdUser': self.createdUser,
        }


class ActivitySign(models.Model):
    '''车友活动报名表'''
    signId = models.AutoField(primary_key=True)
    ridersActivity = models.ForeignKey(RidersActivity, db_column='raId')
    name = models.CharField(max_length=20)
    linkPhone = models.CharField(max_length=20)
    carNo = models.CharField(max_length=20, blank=True, null=True)
    signNum = models.IntegerField()
    status = models.IntegerField()
    createdTime = models.DateTimeField()

    objects = BaseManager()

    class Meta:
        db_table = 'activitySign'
        managed = False
        verbose_name = '活动报名'

        permissions = (
            ('view_activitysign', '活动-报名-查看'),
        )

    def to_dict(self):
        return {
            'id': self.signId,
            'raId': self.ridersActivity.raId,
            'acTitle': self.ridersActivity.acTitle,
            'name': self.name,
            'linkPhone': self.linkPhone,
            'carNo': self.carNo,
            'signNum': self.signNum,
            'createdTime': formattime(self.createdTime)
        }
