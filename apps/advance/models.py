from django.db import models

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime, split_field
from shop.models import Shop
from user.models import User

ADVANCE_TYPE = {
    1: '保养',
    2: '洗车'
}


class AdvanceInfo(models.Model):
    '''预约信息表'''
    infoId = models.AutoField(primary_key=True)
    advanceNo = models.CharField(max_length=20)
    type = models.SmallIntegerField()
    user = models.ForeignKey(User, db_column='userId')
    # shopId = models.IntegerField(blank=True)
    shopNo = models.CharField(max_length=50, blank=True)
    orderTime = models.DateTimeField()
    brandName = models.CharField(max_length=50, blank=True, null=True)
    familyName = models.CharField(max_length=100, blank=True, null=True)
    packageName = models.CharField(max_length=30, blank=True, null=True)
    packageNo = models.CharField(max_length=30, blank=True, null=True)
    reschduleTime = models.DateTimeField(blank=True, null=True)
    reschduleDesc = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    updatedTime = models.DateTimeField(blank=True, null=True)

    objects = BaseManager()

    def __init__(self, *args, **kwargs):
        self._shopName = None
        super(AdvanceInfo, self).__init__(*args, **kwargs)

    class Meta:
        db_table = 'advanceInfo'
        managed = False
        verbose_name = '预约'

        permissions = (
            ('view_advanceinfo', '预约-查看'),
        )

    @property
    def shopName(self):
        if not self._shopName:
            try:
                shopName = Shop.objects.filter(fiveSysId=self.shopNo).values_list('shopName', flat=True)[0]
                self._shopName = shopName
            except:
                pass
        return self._shopName

    def to_dict(self, shopName=''):
        return {
            'id': self.infoId,
            'advanceNo': self.advanceNo,
            'type': ADVANCE_TYPE.get(self.type, ''),
            'userId': self.user.userId,
            'userName': self.user.userName,
            'shopNo': self.shopNo,
            'shopName': shopName,
            'orderTime': formattime(self.orderTime),
            'packageName': self.packageName,
            'packageNo': self.packageNo,
            'reschduleTime': formattime(self.reschduleTime),
            'reschduleDesc': self.reschduleDesc,
            'remark': self.remark,
            'status': self.status,
            'createdTime': formattime(self.createdTime),
        }
