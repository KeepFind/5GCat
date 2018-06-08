# coding:utf-8
import calendar
from datetime import datetime, timedelta

from django.db.models import Sum
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from account.models import PayOrder, WithdrawOrder
from common.db import raw_sql
from common.http import JSONResponse
from common.string_extension import thousandth, increase_rate, cache_seconds, cast_none
from user.models import User

t_expires = cache_seconds(datetime.now(), 10)  # 今日数据 缓存过期时间


@csrf_exempt
def get_main_stats(request):
    start = now().date()
    end = start + timedelta(days=1)
    y_start = start + timedelta(days=-1)
    y_end = end + timedelta(days=-1)
    tomorrow = datetime(start.year, start.month, start.day) + timedelta(days=1)
    y_expires = (tomorrow - datetime.now()).seconds  # 昨日数据 缓存过期时间

    data = dict()

    # 昨日注册用户数
    y_registCount = cache.get('y_registCount')
    if y_registCount is None:
        y_registCount = User.objects.filter(registerTime__range=(y_start, y_end)).count()
        cache.set('y_registCount', y_registCount, y_expires)

    # 今日注册用户数
    t_registCount = cache.get('t_registCount')
    if t_registCount is None:
        t_registCount = User.objects.filter(registerTime__range=(start, end)).count()
        cache.set('t_registCount', t_registCount, t_expires)
    data['registCount'] = t_registCount
    data['registRate'] = increase_rate(y_registCount, t_registCount)

    # 昨日日活
    y_dau = cache.get('y_dau')
    if y_dau is None:
        y_dau = data['y_dau'] = User.objects.filter(lastLoginTime__range=(y_start, y_end)).count()
        cache.set('y_dau', y_dau, y_expires)

    # 今日日活
    t_dau = cache.get('t_dau')
    if t_dau is None:
        t_dau = User.objects.filter(lastLoginTime__range=(start, end)).count()
        cache.set('t_dau', t_dau, t_expires)

    data['dau'] = t_dau
    data['dauRate'] = increase_rate(y_dau, t_dau)

    # 昨日充值金额
    y_payamount = cache.get('y_payamount')
    if y_payamount is None:
        y_payamount = PayOrder.objects.filter(payTime__range=(y_start, y_end), orderStatus=2) \
            .aggregate(payAmount=Sum('payAmount'))['payAmount']
        cache.set('y_payamount', cast_none(y_payamount), y_expires)

    # 今日充值金额
    t_payamount = cache.get('t_payamount')
    if t_payamount is None:
        t_payamount = PayOrder.objects.filter(payTime__range=(start, end), orderStatus=2) \
            .aggregate(payAmount=Sum('payAmount'))['payAmount']
        cache.set('t_payamount', cast_none(t_payamount), t_expires)

    data['payAmount'] = thousandth(t_payamount)
    data['payRate'] = increase_rate(y_payamount, t_payamount)

    # 昨日提现金额
    y_withdrawamount = cache.get('y_withdraw_amount')
    if y_withdrawamount is None:
        y_withdrawamount = WithdrawOrder.objects.filter(wrTime__range=(y_start, y_end), orderStatus=1) \
            .aggregate(withdrawAmount=Sum('wrMoney'))['withdrawAmount']
        cache.set('y_withdraw_amount', cast_none(y_withdrawamount), y_expires)

    # 今日提现金额
    t_withdrawamount = cache.get('t_withdrawamount')
    if t_withdrawamount is None:
        t_withdrawamount = WithdrawOrder.objects.filter(wrTime__range=(start, end), orderStatus=1) \
            .aggregate(withdrawAmount=Sum('wrMoney'))['withdrawAmount']
        cache.set('t_withdrawamount', cast_none(t_withdrawamount), t_expires)

    data['withdrawAmount'] = thousandth(t_withdrawamount)
    data['withdrawRate'] = increase_rate(y_withdrawamount, t_withdrawamount)

    return JSONResponse(data)


@csrf_exempt
def get_month_userstats(request):
    '''月注册用户'''
    year = now().year
    month = now().month

    # 月注册数据
    m_registCharts = cache.get('m_registCharts')
    if m_registCharts is None:
        m_registCharts = raw_sql("""SELECT date_format(dday,'%Y-%m-%d') registerDate,count(*)-1 as num
        FROM( SELECT datelist as dday FROM calendar  where year(datelist)={0} and month(datelist)={1}
            UNION ALL SELECT date(registerTime) FROM user where year(registerTime)={0} and month(registerTime)={1}
        ) a GROUP BY registerDate""".format(year, month))
        cache.set('m_registCharts', m_registCharts, t_expires)

    return JSONResponse(m_registCharts)


@csrf_exempt
def get_month_orderstats(request):
    '''月充值、提现'''
    year = now().year
    month = now().month

    # 月充值数据
    m_payCharts = cache.get('m_payCharts')
    if m_payCharts is None:
        m_payCharts = raw_sql("""SELECT date_format(dday, '%Y-%m-%d') payDate,
          sum(payAmount) as amount FROM
          (SELECT  datelist as dday ,'payAmount' FROM calendar 
          where year(datelist) = {0} and month(datelist) = {1} UNION ALL 
          SELECT  date(payTime),payAmount FROM payOrder where year(payTime) = {0} and month(payTime) = {1}) a 
          GROUP BY payDate""".format(year, month))
        cache.set('m_payCharts', m_payCharts, t_expires)

    # 月提现数据
    m_withdrawCharts = cache.get('m_withdrawCharts')
    if m_withdrawCharts is None:
        m_withdrawCharts = raw_sql("""SELECT date_format(dday, '%Y-%m-%d') payDate,
          sum(wrMoney) as amount FROM
          (SELECT  datelist as dday ,'wrMoney' FROM calendar 
          where year(datelist) = {0} and month(datelist) = {1} UNION ALL 
          SELECT  date(wrTime),wrMoney FROM withdrawOrder  where year(wrTime) = {0} and month(wrTime) = {1}) a 
          GROUP BY payDate""".format(year, month))
        cache.set('m_withdrawCharts', m_withdrawCharts, t_expires)

    data = {'payAmounts': m_payCharts, 'withdrawAmounts': m_withdrawCharts}

    return JSONResponse(data)


@csrf_exempt
def get_month_totalstats(request):
    '''月总的数据'''
    year = now().year
    month = now().month
    weeks, days = calendar.monthrange(year, month)
    month_end = datetime(year, month, days, 23, 58)
    lastmonth_expires = (month_end - datetime.now()).seconds

    data = dict()

    # 上月注册用户数
    lastmonth_registcount = cache.get('lastmonth_registcount')
    if lastmonth_registcount is None:
        lastmonth_registcount = User.objects.raw("""select userId,count(userId) as num from user \
          where date_format(registerTime,'%%Y-%%m')=date_format(DATE_SUB(curdate(), INTERVAL 1 MONTH),'%%Y-%%m') """)[0].num
        cache.set('lastmonth_registcount', cast_none(lastmonth_registcount), lastmonth_expires)

    # 本月注册用户数
    registcount = cache.get('registcount')
    if registcount is None:
        registcount = User.objects.filter(registerTime__year=year, registerTime__month=month).count()
        cache.set('registcount', registcount, t_expires)

    data['registCount'] = registcount
    data['registRate'] = increase_rate(lastmonth_registcount, registcount)

    # 上月充值金额
    lastmonth_pay = cache.get('lastmonth_pay')
    if lastmonth_pay is None:
        lastmonth_pay = PayOrder.objects.raw("""select poId,SUM(payAmount) as total from payOrder \
              where date_format(payTime,'%%Y-%%m')=date_format(DATE_SUB(curdate(), INTERVAL 1 MONTH),'%%Y-%%m')""")[0].total
        cache.set('lastmonth_pay', cast_none(lastmonth_pay), lastmonth_expires)

    # 本月充值金额
    payamount = cache.get('payamount')
    if payamount is None:
        payamount = PayOrder.objects.filter(payTime__year=year, payTime__month=month, orderStatus=2) \
            .aggregate(payAmount=Sum('payAmount'))['payAmount']
        cache.set('payamount', cast_none(payamount), t_expires)

    data['payAmount'] = thousandth(payamount)
    data['payRate'] = increase_rate(lastmonth_pay, payamount)

    # 上月提现金额
    lastmonth_withdraw = cache.get('lastmonth_withdraw')
    if lastmonth_withdraw is None:
        lastmonth_withdraw = WithdrawOrder.objects.raw("""SELECT wrId,SUM(wrMoney) AS total FROM withdrawOrder \
                 WHERE DATE_FORMAT(wrTime,'%%Y-%%m')=DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH),'%%Y-%%m')""")[0].total
        cache.set('lastmonth_withdraw', cast_none(lastmonth_withdraw), lastmonth_expires)

    # 本月提现金额
    withdrawamount = cache.get('withdrawamount')
    if withdrawamount is None:
        withdrawamount = WithdrawOrder.objects.filter(wrTime__year=year, wrTime__month=month, orderStatus=1) \
            .aggregate(withdrawAmount=Sum('wrMoney'))['withdrawAmount']
        cache.set('withdrawamount', cast_none(withdrawamount), t_expires)

    data['withdrawAmount'] = thousandth(withdrawamount)
    data['withdrawRate'] = increase_rate(lastmonth_withdraw, withdrawamount)

    return JSONResponse(data)
