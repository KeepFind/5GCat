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
            name='AdvanceInfo',
            fields=[
                ('infoId', models.AutoField(primary_key=True, serialize=False)),
                ('advanceNo', models.CharField(max_length=20)),
                ('type', models.SmallIntegerField()),
                ('orderTime', models.DateTimeField()),
                ('packageName', models.CharField(blank=True, max_length=30, null=True)),
                ('packageNo', models.CharField(blank=True, max_length=30, null=True)),
                ('thirdNo', models.CharField(blank=True, max_length=30, null=True)),
                ('reschduleTime', models.DateTimeField(blank=True, null=True)),
                ('reschduleDesc', models.TextField(blank=True, null=True)),
                ('remark', models.TextField(blank=True, null=True)),
                ('status', models.IntegerField()),
                ('createdTime', models.DateTimeField()),
                ('updatedTime', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '预约',
                'permissions': (('view_advanceinfo', '预约-查看'),),
                'db_table': 'advanceInfo',
                'managed': False,
            },
        ),
    ]
