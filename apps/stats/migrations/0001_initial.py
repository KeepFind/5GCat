# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-27 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiveMoney',
            fields=[
                ('clId', models.AutoField(primary_key=True, serialize=False)),
                ('consumerType', models.IntegerField()),
                ('money', models.DecimalField(decimal_places=2, max_digits=20)),
                ('policyNo', models.CharField(blank=True, max_length=50, null=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('payType', models.IntegerField(blank=True, null=True)),
                ('payTime', models.DateTimeField(blank=True, null=True)),
                ('status', models.IntegerField()),
                ('createdTime', models.DateTimeField()),
            ],
            options={
                'verbose_name': '收款',
                'permissions': (('view_receivemoney', '结算-查看'),),
                'db_table': 'receiveMoney',
                'managed': False,
            },
        ),
    ]
