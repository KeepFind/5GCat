from django.db import models

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime


class Headline(models.Model):
    '''头条表'''
    headlineId = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20)
    body = models.TextField()
    imgUrl = models.CharField(max_length=80, blank=True, null=True)
    status = models.IntegerField()
    intro = models.CharField(max_length=100, blank=True, null=True)
    thumbnailUrl = models.CharField(max_length=255, blank=True, null=True)
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    objects = BaseManager()

    class Meta:
        db_table = 'headline'
        managed = False
        verbose_name = '头条'

        permissions = (
            ('view_headline', '内容-头条-查看'),
        )

    def to_dict(self):
        return {
            'id': self.headlineId,
            'title': self.title,
            'body': self.body,
            'imgUrl': self.imgUrl,
            'status': self.status,
            'createdTime': formattime(self.createdTime),
        }
