# coding:utf-8
import os

'''
@summary: 用户自定义全局常量设置
'''

# ===============================================================================
# 静态资源
# ===============================================================================
# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存, 可能会造成没更新的情况.
# 所以在引用静态资源的地方，都把这个加上，如：<script src="/a.js?v=${STATIC_VERSION}"></script>；
# 如果静态资源修改了以后，上线前改这个版本号即可
STATIC_VERSION = 1.0

# ===============================================================================
# debug toolbar 配置
# ===============================================================================
DEBUG_TOOLBAR_PATCH_SETTINGS = False
DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': "http://code.jquery.com/jquery-2.1.1.min.js"
}

# ===============================================================================
# 七牛配置
# ===============================================================================
QINIU_ACCESS_KEY = 'I353bEqRJxcTr3bw6OEaONQkeKbxwmKH86w1Xhdo'
QINIU_SECRET_KEY = 'd-oqhIv3b7JAi3QB9d1wwaGsZL4DUpzOvcto3vTO'
QINIU_DOMAIN = 'http://orsbtd7g6.bkt.clouddn.com'
QINIU_BUCKET = 'detection-5g'

# 内网ip列表
INTERNAL_IPS = ['127.0.0.1']

# ==============================================================================
# 中间件和应用
# ==============================================================================
# 自定义中间件
MIDDLEWARE_CLASSES_CUSTOM = [
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

# 自定义APP
INSTALLED_APPS_CUSTOM = [
    # add your app here...
    # Note: 请注意在第一次syncdb时不加自己的app
    'debug_toolbar',

    'manage',
    'activity',
    'advance',
    'ad',
    'obd',
    'stats',
    'article',
    'user',
    'shop',
    'account',
    'upload',
]

# ===============================================================================
# 日志级别
# ===============================================================================
# 本地开发环境日志级别
LOG_LEVEL_DEVELOP = 'DEBUG'
# 正式环境日志级别
LOG_LEVEL_PRODUCT = os.environ.get('LOG_LEVEL', 'ERROR')

# ===============================================================================
# 缩略图尺寸
# ===============================================================================
HEADLINE_THUMB = 'imageView2/1/w/200/h/200/'  # 头条封面缩略图
