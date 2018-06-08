from django.db import models

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime
from user.models import User

WITHDRAW_STATUS = {
    0: '待审核',
    1: '审核通过',
    2: '审核不通过',
    3: '交易成功',
    4: '交易失败',
}

ACCTYPE = {
    0: '微信',
    1: '支付宝',
    2: '银行卡',
}


class WithdrawOrder(models.Model):
    '''提现订单表'''
    wrId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='userId')
    wrMoney = models.DecimalField(max_digits=20, decimal_places=2)
    procedureRates = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    wrTime = models.DateTimeField(blank=True, null=True)
    accType = models.SmallIntegerField(blank=True, null=True)
    accountNo = models.CharField(max_length=30)
    bankName = models.CharField(max_length=20)
    cardType = models.CharField(max_length=20)
    cardholder = models.CharField(max_length=20)
    orderStatus = models.SmallIntegerField()
    channelNo = models.CharField(max_length=30, blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()

    objects = BaseManager()

    class Meta:
        db_table = 'withdrawOrder'
        managed = False
        verbose_name = '提现'

        default_permissions = []
        permissions = (
            ('view_withdraworder', '账务-提现-查看'),
            ('audit_withdraworder', '账务-提现-审核'),
        )

    def to_dict(self):
        return {
            'id': self.wrId,
            'userId': self.user.userId,
            'userName': self.user.userName,
            'wrMoney': self.wrMoney,
            'procedureRates': self.procedureRates,
            'wrTime': formattime(self.wrTime),
            'accType': ACCTYPE.get(self.accType) if self.accType else '',
            'accountNo': self.accountNo,
            'bankName': self.bankName,
            'cardType': self.cardType,
            'cardholder': self.cardholder,
            'orderStatus': WITHDRAW_STATUS.get(self.orderStatus, ''),
            'channelNo': self.channelNo,
            'remark': self.remark,
        }


class Accountlog(models.Model):
    '''账单表'''
    logId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='userId')
    accountTime = models.DateTimeField()
    accountType = models.SmallIntegerField()
    money = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=50)
    rechargeBalance = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    currentBalance = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        db_table = 'accountLog'
        managed = False
        verbose_name = '账单'
        default_permissions = []


class PayInfo(models.Model):
    '''充值产品信息表'''
    piId = models.AutoField(primary_key=True)
    rechargeAmount = models.DecimalField(max_digits=20, decimal_places=2)
    awardAmount = models.DecimalField(max_digits=20, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    objects = BaseManager()

    class Meta:
        db_table = 'payInfo'
        managed = False
        verbose_name = '充值产品'

        permissions = (
            ('view_payinfo', '账务-充值产品-查看'),
        )

    def to_dict(self):
        return {
            'id': self.piId,
            'rechargeAmount': self.rechargeAmount,
            'awardAmount': self.awardAmount,
            'description': self.description,
            'status': self.status,
            'createdTime': formattime(self.createdTime),
            # 'createdUserId': self.createdUser.userId,
            'createdUser': self.createdUser,
        }


PAYORDER_STATUS = {
    1: '待支付',
    2: '支付成功',
    3: '支付失败'
}

CHANNEL = {
    '1': '微信',
    '2': '银行卡',
    '3': '支付宝'
}


class PayOrder(models.Model):
    '''充值订单表'''
    poId = models.AutoField(primary_key=True)
    payOrderNo = models.CharField(max_length=20)
    user = models.ForeignKey(User, db_column='userId')
    payAmount = models.DecimalField(max_digits=20, decimal_places=2)
    awardAmount = models.DecimalField(max_digits=20, decimal_places=2)
    channel = models.CharField(max_length=20)
    channelAccount = models.CharField(max_length=20)
    channelNo = models.CharField(max_length=30, blank=True, null=True)
    payTime = models.DateTimeField(blank=True, null=True)
    payInfo = models.ForeignKey(PayInfo, db_column='piId')
    orderStatus = models.SmallIntegerField()
    productName = models.CharField(max_length=20)
    status = models.IntegerField()
    createdTime = models.DateTimeField()

    class Meta:
        db_table = 'payOrder'
        managed = False
        verbose_name = '充值'

        permissions = (
            ('view_payorder', '账务-充值-查看'),
        )

    def to_dict(self):
        return {
            'id': self.poId,
            'payOrderNo': self.payOrderNo,
            'userId': self.user.userId,
            'userName': self.user.userName,
            'payAmount': self.payAmount,
            'awardAmount': self.awardAmount,
            'channel': CHANNEL.get(self.channel),
            'payTime': formattime(self.payTime),
            'piId': self.payInfo.piId,
            'productName': self.productName,
            'orderStatus': PAYORDER_STATUS.get(self.orderStatus, ''),
            'createdTime': formattime(self.createdTime),
        }


class AwardRecord(models.Model):
    '''充值推荐奖励记录表'''
    arId = models.AutoField(primary_key=True)
    payOrder = models.ForeignKey(PayOrder, db_column='poId', blank=True, null=True)
    user = models.ForeignKey(User, db_column='userId', blank=True, null=True)
    firstAward = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    secondAward = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    threeAward = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    fourAward = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    fiveAward = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    communityAmount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    createdTime = models.DateTimeField()
    status = models.IntegerField()

    class Meta:
        db_table = 'awardRecord'
        managed = False
        verbose_name = '充值推荐奖励'
        default_permissions = []

    def to_dict(self):
        return {
            'id': self.arId,
            'payOrderNo': self.payOrder.payOrderNo,
            'userId': self.user.userId,
            'userName': self.user.userName,
            'payAmount': self.payOrder.payAmount,
            'firstAward': self.firstAward,
            'secondAward': self.secondAward,
            'threeAward': self.threeAward,
            'firstUserId': '',
            'firstUserName': '',
            'secondUserId': '',
            'secondUserName': '',
            'thirdUserId': '',
            'thirdUserName': '',
            'createdTime': formattime(self.createdTime),
        }
