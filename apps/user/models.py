from django.db import models

from common.model_manager import BaseManager
from common.string_extension import formattime, formatdate
from shop.models import Shop

USER_STATUS = (
    ('')
)


class UserManager(BaseManager, models.Manager):
    def get_id_name(self, userId):
        if userId:
            result = self.filter(userId=userId).values('userId', 'userName')
            if result:
                result = result[0]
            return result
        return None


class User(models.Model):
    '''用户表'''
    userId = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=30)
    password = models.CharField(max_length=32)
    registerTime = models.DateTimeField()
    failureNumber = models.SmallIntegerField()
    lastLoginTime = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()

    objects = UserManager()

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        try:
            self.userInfo = UserInfo.objects.get(user_id=self.userId)
        except:
            self.userInfo = None

    class Meta:
        db_table = 'user'
        managed = False
        verbose_name = '用户'

        permissions = (
            ('view_user', '车主-查看'),
        )

    def to_dict(self):
        return {
            'id': self.userId,
            'userName': self.userName,
            'shopId': '',
            'shopName': '',
            'registerTime': formattime(self.registerTime),
            'status': self.status,
            'lastLoginTime': formattime(self.lastLoginTime),
        }


class UserInfo(models.Model):
    '''用户信息表'''
    infoId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='userId')
    payPwd = models.CharField(db_column='payPwd', max_length=12, blank=True, null=True)
    awardBalance = models.DecimalField(max_digits=20, decimal_places=2)
    rechargeBalance = models.DecimalField(max_digits=20, decimal_places=2)
    referralUser = models.ForeignKey(User, related_name='referralUserId', db_column='referralUserId', blank=True,
                                     null=True)
    referralCode = models.CharField(max_length=6, blank=True, null=True)
    userImg = models.CharField(max_length=80, blank=True, null=True)
    nickname = models.CharField(max_length=20, blank=True, null=True)
    gender = models.NullBooleanField(blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    signature = models.CharField(max_length=50, blank=True, null=True)
    age = models.SmallIntegerField(blank=True, null=True)
    constellation = models.CharField(max_length=20, blank=True, null=True)
    height = models.SmallIntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    job = models.CharField(max_length=20, blank=True, null=True)
    hobby = models.CharField(max_length=50, blank=True, null=True)
    defaultShopId = models.IntegerField(blank=True, null=True)
    updatedTime = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        db_table = 'userInfo'
        managed = False
        verbose_name = '用户信息'

        default_permissions = []

    def to_dict(self):
        return {
            'id': self.user.userId,
            'userName': self.user.userName,
            'shopId': self.defaultShopId,
            'shopName': '',
            'registerTime': formattime(self.user.registerTime),
            'status': self.user.status,
            'lastLoginTime': formattime(self.user.lastLoginTime),
        }


class UserRecommendStatistical(models.Model):
    '''用户推荐统计表'''
    ursId = models.IntegerField(primary_key=True)
    referral = models.ForeignKey(User, db_column='referralId', blank=True, null=True)
    byReferreal = models.ForeignKey(User, related_name='byReferrealId', db_column='byReferrealId', blank=True,
                                    null=True)
    award = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    community = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        db_table = 'userRecommendStatistical'
        managed = False
        verbose_name = '用户推荐统计'

        default_permissions = []


class RecommendRelate(models.Model):
    '''用户推荐信息表'''
    relateId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='userId')
    firstUserId = models.IntegerField(blank=True, null=True)
    secondUserId = models.IntegerField(blank=True, null=True)
    threeUserId = models.IntegerField(blank=True, null=True)
    fourUserId = models.IntegerField(blank=True, null=True)
    fiveUserId = models.IntegerField(blank=True, null=True)
    recommendTotal = models.IntegerField(blank=True, null=True)
    communityTotal = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    awardTotal = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    status = models.IntegerField()

    class Meta:
        db_table = 'recommendRelate'
        managed = False
        verbose_name = '用户推荐'

        default_permissions = []


class ThirdAccount(models.Model):
    '''第三方账号表'''
    tacId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='userId')
    accType = models.SmallIntegerField(blank=True, null=True)
    accountNo = models.CharField(max_length=30)
    bankName = models.CharField(max_length=20)
    cardType = models.CharField(max_length=20)
    realName = models.CharField(max_length=20)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    updatedTime = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'thirdAccount'
        managed = False
        verbose_name = '第三方账号'

        default_permissions = []


INFOTYPE = {
    1: '小型车'
}


class CarInfo(models.Model):
    '''车辆信息表'''
    carId = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, db_column='userId')
    infoType = models.SmallIntegerField()
    carNoFix = models.CharField(max_length=1)
    carNo = models.CharField(max_length=20)
    vin = models.CharField(max_length=30, blank=True, null=True)
    engineNo = models.CharField(max_length=50, blank=True, null=True)
    ownerNo = models.CharField(max_length=20, blank=True, null=True)
    owner = models.CharField(max_length=20, blank=True, null=True)
    configType = models.CharField(max_length=50, blank=True, null=True)
    brandType = models.CharField(max_length=30, blank=True, null=True)
    annualSurveyDate = models.DateField(blank=True, null=True)
    insuranceDate = models.DateField(blank=True, null=True)
    registerDate = models.DateField(blank=True, null=True)
    mileage = models.IntegerField(blank=True, null=True)
    drivingPermitUrl = models.CharField(max_length=80, blank=True, null=True)
    identityCardUrl = models.CharField(max_length=80, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    updatedTime = models.DateTimeField(blank=True, null=True)
    brandName = models.CharField(max_length=50, blank=True, null=True)
    familyName = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'carInfo'
        managed = False
        verbose_name = '车辆'

        default_permissions = []
        permissions = (
            ('view_carinfo', '车主-车辆-查看'),
        )

    def to_dict(self):
        return {
            'id': self.carId,
            'userId': self.user.userId,
            'userName': self.user.userName,
            'infoType': INFOTYPE.get(self.infoType, ''),
            'carNoFix': self.carNoFix,
            'carNo': self.carNo,
            'vin': self.vin,
            'engineNo': self.engineNo,
            'owner': self.owner,
            'annualSurveyDate': formatdate(self.annualSurveyDate),
            'insuranceDate': formatdate(self.insuranceDate),
            'registerDate': formattime(self.registerDate),
            'createdTime': formattime(self.createdTime),
        }


class CarBrand(models.Model):
    brand_id = models.IntegerField(primary_key=True)
    brand_name = models.CharField(max_length=200)
    brand_letter = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'carbrand'

    def to_dict(self):
        return {
            'id': self.brand_id,
            'text': self.brand_name,
        }


class CarSeries(models.Model):
    '''车系表'''
    series_id = models.IntegerField(primary_key=True)
    series_name = models.CharField(max_length=200)
    series_group_name = models.CharField(max_length=200)
    brand_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'carseries'

    def to_dict(self):
        return {
            'id': self.series_id,
            'text': self.series_name,
            'series_group_name': self.series_group_name,
            'brand_id': self.brand_id
        }


class CarModel(models.Model):
    '''车型表'''
    model_id = models.IntegerField(primary_key=True)
    model_name = models.CharField(max_length=200)
    series_id = models.IntegerField()
    model_price = models.DecimalField(max_digits=18, decimal_places=2)
    model_year = models.CharField(max_length=20)
    min_reg_year = models.CharField(max_length=20)
    max_reg_year = models.CharField(max_length=20)
    liter = models.CharField(max_length=20)
    liter_type = models.CharField(max_length=20)
    gear_type = models.CharField(max_length=20)
    discharge_standard = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'carmodel'

    def to_dict(self):
        return {
            'id': self.model_id,
            'text': self.model_name,
            'series_id': self.series_id,
            'model_price': self.model_price,
            'model_year': self.model_year,
        }
