from django.db import models

# Create your models here.


class Carbrand(models.Model):
    brandid = models.CharField(db_column='brandId', max_length=50)  # Field name made lowercase.
    brandcode = models.CharField(db_column='brandCode', max_length=30)  # Field name made lowercase.
    brandname = models.CharField(db_column='brandName', max_length=30)  # Field name made lowercase.
    brandinitial = models.CharField(db_column='brandInitial', max_length=30)  # Field name made lowercase.
    importflag = models.CharField(db_column='importFlag', max_length=30)  # Field name made lowercase.
    ishotbrand = models.CharField(db_column='isHotBrand', max_length=30, blank=True, null=True)  # Field name made lowercase.
    brandicon = models.CharField(db_column='brandIcon', max_length=30, blank=True, null=True)  # Field name made lowercase.
    updatedtime = models.DateTimeField(db_column='updatedTime', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'carBrand'