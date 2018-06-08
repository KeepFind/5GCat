from django.db import models

# Create your models here.
from common.string_extension import formattime


class ObdDevice(models.Model):
    """OBD设备表"""
    sn = models.CharField(primary_key=True, max_length=50)
    producerName = models.CharField(max_length=100, blank=True, null=True)
    producerAddress = models.CharField(max_length=255, blank=True, null=True)
    producerPhone = models.CharField(max_length=50, blank=True, null=True)
    roductionDate = models.DateTimeField(blank=True, null=True)
    purchaseTime = models.DateTimeField(blank=True, null=True)
    purchaseUser = models.CharField(max_length=20, blank=True, null=True)
    purchasePrice = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ObdDevice'

    def to_dict(self, shopNo=None, shopName='', carId='', carNoFix='', carNo=''):
        return {
            'sn': self.sn,
            'shopNo': shopNo,
            'shopName': shopName,
            'carId': carId,
            'carNoFix': carNoFix,
            'carNo': carNo,
            'producerName': self.producerName,
            'producerAddress': self.producerAddress,
            'producerPhone': self.producerPhone,
            'roductionDate': formattime(self.roductionDate),
            'purchaseTime': formattime(self.purchaseTime),
            'purchaseUser': self.purchaseUser,
            'purchasePrice': self.purchasePrice,
        }


class CarObd(models.Model):
    """车辆OBD关联表"""
    sn = models.CharField(max_length=50)
    shopNo = models.CharField(max_length=50)
    createdTime = models.DateTimeField()
    carId = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'carObd'


class CarRunMessage(models.Model):
    """车辆行驶消息记录表"""
    sn = models.CharField(max_length=50)
    createdTime = models.DateTimeField()
    type = models.SmallIntegerField()
    contents = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'carRunMessage'


class AlarmRecord(models.Model):
    """车辆报警记录表"""
    time = models.DateTimeField()
    address = models.TextField()
    lng = models.DecimalField(max_digits=10, decimal_places=7)
    lat = models.DecimalField(max_digits=10, decimal_places=7)
    type = models.SmallIntegerField()
    voltage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    sn = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'alarmRecord'


class Travelstatistics(models.Model):
    """行程统计表"""
    sn = models.CharField(max_length=50)
    startTime = models.DateTimeField(blank=True, null=True)
    shutdownTime = models.DateTimeField(blank=True, null=True)
    voltage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    runTime = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    runMileage = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    oilWear = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    maxRpm = models.IntegerField(blank=True, null=True)
    maxVelocity = models.IntegerField(blank=True, null=True)
    speedUp = models.SmallIntegerField(blank=True, null=True)
    speedCut = models.SmallIntegerField(blank=True, null=True)
    turn = models.SmallIntegerField(blank=True, null=True)
    oilWearAvg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    totalMileage = models.IntegerField(blank=True, null=True)
    retain = models.TextField(blank=True, null=True)
    createdTime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'travelStatistics'
