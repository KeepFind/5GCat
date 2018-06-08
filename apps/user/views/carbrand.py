from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View

from user.models import CarBrand, CarSeries, CarModel


def get_carbrands(request):
    car_brands = CarBrand.objects.using('carbrand').all().order_by('brand_letter')
    result = [item.to_dict() for item in car_brands]
    return JsonResponse(result, safe=False)


def get_carseries(request):
    brand_id = request.GET.get('brand_id')
    car_series = CarSeries.objects.using('carbrand').filter(brand_id=brand_id)

    result = [item.to_dict() for item in car_series]
    return JsonResponse(result, safe=False)


def get_carmodels(request):
    series_id = request.GET.get('series_id')
    car_models = CarModel.objects.using('carbrand').filter(series_id=series_id).order_by('-model_year')

    result = [item.to_dict() for item in car_models]
    return JsonResponse(result, safe=False)


class CarBrandView(View):
    template_name = 'user/carbrand.html'

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)
