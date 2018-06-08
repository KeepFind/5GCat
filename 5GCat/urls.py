"""GCat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
import debug_toolbar
from manage.views import home, stats

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^debug/', include(debug_toolbar.urls)),

    url(r'^manage/', include('manage.urls', namespace='manage')),  # 管理
    url(r'^user/', include('user.urls', namespace='user')),  # 车主
    url(r'^obd/', include('obd.urls', namespace='obd')),  # OBD
    url(r'^account/', include('account.urls', namespace='account')),  # 财务
    url(r'^shop/', include('shop.urls', namespace='shop')),  # 门店
    url(r'^advance/', include('advance.urls', namespace='advance')),  # 预约
    url(r'^activity/', include('activity.urls', namespace='activity')),  # 活动
    url(r'^article/', include('article.urls', namespace='article')),  # 内容
    url(r'^ad/', include('ad.urls', namespace='ad')),  # 广告
    url(r'^stats/', include('stats.urls', namespace='stats')),  # 结算

    url(r'^upload/', include('upload.urls', namespace='upload')),  # 上传

    url(r'^login/', home.LoginView.as_view(), name='login'),
    url(r'^logout/', home.logout, name='logout'),
    url(r'^401.html', home.unauthorized, name='401'),

    url(r'^welcome/', home.welcome, name='welcome'),
    url(r'^getmainstats/', stats.get_main_stats, name='mainstats'),
    url(r'^getmonthuserstats/', stats.get_month_userstats, name='month_userstats'),
    url(r'^getmonthorderstats/', stats.get_month_orderstats, name='month_orderstats'),
    url(r'^getmonthtotalstats/', stats.get_month_totalstats, name='month_totalstats'),

    url(r'^$', home.index, name='home'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)))
