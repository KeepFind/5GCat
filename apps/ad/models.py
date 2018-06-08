from django.db import models

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime, split_field


class AdpositionManager(BaseManager, models.Manager):
    def get_id_name(self, posiId):
        if posiId:
            result = self.filter(posiId=posiId).values('posiId', 'posiName')
            if result:
                result = result[0]
            return result
        return None


class Adposition(models.Model):
    '''广告位'''
    posiId = models.AutoField(primary_key=True)
    posiName = models.CharField(max_length=20)
    posiNo = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    objects = AdpositionManager()

    class Meta:
        db_table = 'adPosition'
        managed = False
        verbose_name = '广告位'

        permissions = (
            ('view_adposition', '广告-广告位-查看'),
        )

    def to_dict(self):
        return {
            'id': self.posiId,
            'posiName': self.posiName,
            'posiNo': self.posiNo,
            'description': split_field(self.description),
            'status': self.status,
            'createdTime': formattime(self.createdTime),
        }


AD_TYPE = {
    1: '图片',
    2: '文字'
}


class Advertisement(models.Model):
    '''广告表'''
    adId = models.AutoField(primary_key=True)
    adPosition = models.ForeignKey(Adposition, db_column='posiId')
    sortNo = models.SmallIntegerField(blank=True, null=True)
    adType = models.SmallIntegerField()
    title = models.CharField(max_length=80)
    adContents = models.TextField(blank=True, null=True)
    linkUrl = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    objects = BaseManager()

    class Meta:
        db_table = 'advertisement'
        managed = False
        verbose_name = '广告'

        permissions = (
            ('view_advertisement', '广告-查看'),
        )

    def to_dict(self):
        return {
            'id': self.adId,
            'posiId': self.adPosition.posiId,
            'posiName': self.adPosition.posiName,
            'sortNo': self.sortNo,
            'adType': AD_TYPE.get(self.adType),
            'title': self.title,
            'linkUrl': self.linkUrl,
            'createdTime': formattime(self.createdTime),
        }
