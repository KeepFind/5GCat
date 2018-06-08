# coding:utf-8
'''
@summary: 全局常量设置
用于本地开发环境
'''

import os

# ===============================================================================
# 数据库设置, 本地开发数据库设置
# ===============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '5gcat',
        'USER': 'root',
        'PASSWORD': 'liubiao123456',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'options': {
            'MAX_ENTRIES': 10240,
        },
    }
}
