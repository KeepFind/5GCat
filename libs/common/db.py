# coding:utf-8

from django.db import connection


def raw_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchall()
