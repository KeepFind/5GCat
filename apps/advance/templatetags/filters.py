# coding:utf-8

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def is_canceled(value):
    return '已取消' if (value & 2) >> 1 == 1 else '正常'
