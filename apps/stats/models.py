from django.db import models

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime
from shop.models import Shop
from user.models import User

CONSUMERTYPE = {
    1: '洗车',
    2: '保养'
}


class ReceiveMoney(models.Model):
    clId = models.AutoField(primary_key=True)
    shopNo = models.CharField(max_length=50, blank=True)
    consumerType = models.IntegerField()
    money = models.DecimalField(max_digits=20, decimal_places=2)
    policyNo = models.CharField(max_length=50, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, db_column='userId', blank=True, null=True)
    payType = models.IntegerField(blank=True, null=True)
    payTime = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()

    def __init__(self, *args, **kwargs):
        self._shopName = None
        super(ReceiveMoney, self).__init__(*args, **kwargs)

    class Meta:
        managed = False
        db_table = 'receiveMoney'
        verbose_name = '收款'

        default_permissions = []
        permissions = (
            ('view_receivemoney', '结算-查看'),
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

    def to_dict(self, shopName):
        return {
            'id': self.clId,
            'shopNo': self.shopNo,
            'shopName': shopName,
            'userId': self.user.userId,
            'userName': self.user.userName,
            'consumerType': CONSUMERTYPE.get(self.consumerType),
            'money': self.money,
            'policyNo': self.policyNo,
            'status': self.status,
            'payTime': formattime(self.payTime),
            'createdTime': formattime(self.createdTime)
        }
