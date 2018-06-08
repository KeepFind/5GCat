import copy

from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from wechatpy.enterprise import WeChatClient
from wechatpy import WeChatClient
from wechatpy.pay.api import WeChatTransfer

from account.models import PayOrder, WithdrawOrder, AwardRecord
from common.decorators import permission_required2
from common.http import JSONResponse
from common.response import paged_result
from common.string_extension import cast_endtime
from user.models import User, RecommendRelate, ThirdAccount


class PayOrderView(PermissionRequiredMixin, View):
    template_name = 'account/payorder.html'
    permission_required = ('account.view_payorder')

    def get(self, request, *args, **kwargs):
        userId = request.GET.get('userId')
        context = User.objects.get_id_name(userId)

        return render(request, self.template_name, context)


class PayOrderDetailView(View):
    template_name = 'account/payorder_detail.html'

    def get(self, request, *args, orderno):
        model = get_object_or_404(PayOrder, payOrderNo=orderno)
        return render(request, self.template_name, {'model': model.to_dict()})


def get_payorders(request):
    ''' 获取充值列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    userId = request.GET.get('userId')
    payStart = request.GET.get('payStart')
    payEnd = request.GET.get('payEnd')

    orders = PayOrder.objects.all()
    if userId:
        orders = orders.filter(user__userId=userId)
    if payStart:
        orders = orders.filter(payTime__gte=payStart)
    if payEnd:
        orders = orders.filter(payTime__lt=cast_endtime(payEnd))

    count = orders.count()  # 总数
    orders = orders.order_by('-createdTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in orders]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


class WithdrawOrderView(PermissionRequiredMixin, View):
    template_name = 'account/withdraworder.html'
    permission_required = ('account.view_withdraworder')

    def get(self, request, *args, **kwargs):
        userId = request.GET.get('userId')
        context = User.objects.get_id_name(userId)
        return render(request, self.template_name, context)


class WithdrawOrderDetailView(View):
    template_name = 'account/withdraworder_detail.html'

    def get(self, request, *args, id):
        model = get_object_or_404(WithdrawOrder, wrId=id)
        return render(request, self.template_name, {'model': model.to_dict()})


@csrf_exempt
@permission_required2('audit_withdraworder')
@require_http_methods(['POST'])
def audit_withdraworder(request):
    id = request.POST.get('id')
    flag = request.POST.get('flag')

    try:
        order = WithdrawOrder.objects.get(wrId=id)
        if order.orderStatus != 0:
            return JSONResponse(msg='无法审核', success=False)

        order.orderStatus = 1 if flag else 0
        order.save()
        return JSONResponse(msg='操作成功', success=True)
    except:
        return JSONResponse(msg='无法审核', success=False)


def get_withdraworders(request):
    ''' 获取提现列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    userId = request.GET.get('userId')
    createStart = request.GET.get('createStart')
    createEnd = request.GET.get('createEnd')

    orders = WithdrawOrder.objects.all()
    if userId:
        orders = WithdrawOrder.objects.filter(user__userId=userId)
    if createStart:
        orders = orders.filter(wrTime__gte=createStart)
    if createEnd:
        orders = orders.filter(wrTime__lt=cast_endtime(createEnd))

    count = orders.count()  # 总数
    users = orders.order_by('-wrTime')[(page - 1) * pagesize:page * pagesize]
    result = [item.to_dict() for item in users]

    paged_result.set(page, pagesize, count, result)

    return JsonResponse(paged_result.to_dict())


class AwardRecordView(View):
    template_name = 'account/awardrecord.html'

    def get(self, request, *args, **kwargs):
        poId = request.GET.get('poId')
        context = {'poId': poId}
        return render(request, self.template_name, context)


def get_awardrecords(request):
    ''' 获取充值推荐奖励列表 '''
    page = int(request.GET.get('page', 1))
    pagesize = int(request.GET.get('rows', 15))
    poId = request.GET.get('poId')

    awards = []
    if poId:
        try:
            award = AwardRecord.objects.get(payOrder__poId=poId)
            recommend = RecommendRelate.objects.get(user__userId=award.user.userId)
        except Exception as e:
            pass
        else:
            award = award.to_dict()

            first_user = safe_id_name(recommend.firstUserId)
            second_user = safe_id_name(recommend.secondUserId)
            third_user = safe_id_name(recommend.threeUserId)

            award['firstUserId'] = first_user['userId']
            award['firstUserName'] = first_user['userName']
            award['secondUserId'] = second_user['userId']
            award['secondUserName'] = second_user['userName']
            award['thirdUserId'] = third_user['userId']
            award['thirdUserName'] = third_user['userName']

            awards = [award]

    count = len(awards)  # 总数
    paged_result.set(page, pagesize, count, awards)

    return JsonResponse(paged_result.to_dict())


def safe_id_name(userId):
    user = User.objects.get_id_name(userId)
    return user if user else {'userId': '', 'userName': ''}


def enterprise_payment(request, wrId):
    order = WithdrawOrder.objects.get(wrId=wrId)
    account = ThirdAccount.objects.get(user__userId=order.user.userId, accType=1)

    client = WeChatClient(settings.WECHAT_APPID, settings.WECHAT_SECRET)
    transfer = WeChatTransfer(client)

    result = transfer.transfer(account.accountNo, order.wrMoney * 100, '提现')

    return HttpResponse('success')
