# coding:utf-8
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View

from common.response import paged_result
from user.models import User, CarInfo


class CarView(PermissionRequiredMixin, View):
    template_name = 'user/car.html'
    permission_required = ('user.view_carinfo')

    def get(self, request, *args, **kwargs):
        userId = request.GET.get('userId')
        context = User.objects.get_id_name(userId)
        return render(request, self.template_name, context)


class CarDetailView(View):
    template_name = 'user/car_detail.html'

    def get(self, request, *args, id):
        car = get_object_or_404(CarInfo, carId=id)
        return render(request, self.template_name, {'model': car.to_dict()})


def get_cars(request):
    ''' 获取车辆列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    userId = request.GET.get('userId')
    carNo = request.GET.get('carNo')

    cars = CarInfo.objects.all()
    if userId:
        cars = cars.filter(user__userId=userId)
    if carNo:
        cars = cars.filter(carNo__icontains=carNo)

    count = cars.count()  # 总数
    users = cars.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in users]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())
