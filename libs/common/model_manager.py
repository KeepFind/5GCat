#coding:utf-8

from django.db import models

class BaseManager(models.Manager):
    def get_queryset(self):
        table_name=self.model._meta.db_table
        where_condition= '{0}.status & 1=0'.format(table_name)
        return super(BaseManager, self).get_queryset().extra(where=[where_condition])