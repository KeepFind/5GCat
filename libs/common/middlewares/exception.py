# coding:utf-8
import sys
from django.conf import settings
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
from django.views.debug import technical_500_response
from common.log import logger


class Exception(MiddlewareMixin):
    def process_exception(self, request, exception):
        if settings.DEBUG:
            return None

        logger.error('request url:' + request.path + '\r' + str(exception))
        return render(request, '500.html')


class UserBasedExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if request.user.is_superuser or request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
            return technical_500_response(request, *sys.exc_info())
