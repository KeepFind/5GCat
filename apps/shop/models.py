from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.db import models
from django.utils import six
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from common.model_manager import BaseManager
from common.string_extension import formattime


class ShopManager(BaseManager, models.Manager):
    def get_id_name(self, shopNo):
        if shopNo:
            result = self.filter(fiveSysId=shopNo).values('fiveSysId', 'shopName')
            if result:
                result = result[0]
                return {'shopNo': result['fiveSysId'], 'shopName': result['shopName']}
        return None


class Shop(models.Model):
    shopId = models.AutoField(primary_key=True)
    shopName = models.CharField(max_length=30)
    linkman = models.CharField(max_length=20, blank=True, null=True)
    provinceId = models.IntegerField(blank=True, null=True)
    province = models.CharField(max_length=20, blank=True, null=True)
    cityId = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    districtId = models.IntegerField(blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    lng = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    sosLinkman = models.CharField(max_length=20, blank=True, null=True)
    sosPhone = models.CharField(max_length=20, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)
    fiveSysId = models.CharField(max_length=32, blank=True, null=True)

    objects = ShopManager()

    class Meta:
        db_table = 'shop'
        managed = False
        verbose_name = '门店'

        permissions = (
            ('view_shop', '门店-查看'),
        )

    def to_dict(self):
        return {
            'id': self.shopId,
            'shopNo': self.fiveSysId,
            'shopName': self.shopName,
            'linkman': self.linkman,
            'address': self.address,
            'phone': self.phone,
            'lng': self.lng,
            'lat': self.lat,
            'sosLinkman': self.sosLinkman,
            'sosPhone': self.sosPhone,
            'status': self.status,
            'createdTime': formattime(self.createdTime),
            'createdUser': self.createdUser,
            'updatedTime': formattime(self.updatedTime),
            'updatedUser': self.updatedUser
        }


class ShopImg(models.Model):
    imgId = models.AutoField(db_column='imgId', primary_key=True)
    shop = models.ForeignKey(Shop, db_column='shopId')
    imgUrl = models.CharField(max_length=80)
    imgDesc = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField()
    createdTime = models.DateTimeField()
    createdUser = models.CharField(max_length=20)
    updatedTime = models.DateTimeField(blank=True, null=True)
    updatedUser = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shopImg'
        verbose_name = '门店图片'

        default_permissions = []


class AuthShopManager(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    avatar = models.URLField(null=True)
    email = models.EmailField(max_length=254, default='')
    shopNo = models.CharField(max_length=50, blank=True)
    mobile = models.CharField(max_length=20, null=True)
    gender = models.NullBooleanField(max_length=40, null=True)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    date_joined = models.DateTimeField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        managed = False
        db_table = 'auth_shopmanager'
        verbose_name = '门店管理员'

        permissions = (
            ('view_auth_shopmanager', '门店-门店管理员-查看'),
        )

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

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
            'id': self.id,
            'username': self.username,
            'shopNo': self.shopNo,
            'shopName': shopName,
            'status': 0,
            'date_joined': formattime(self.date_joined),
        }
