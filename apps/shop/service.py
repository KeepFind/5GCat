# coding:utf-8
from datetime import datetime

from django.db import transaction

from common.upload import qiniu_upload
from shop.models import Shop, ShopImg


def save_shop(shop: Shop, img_files):
    '''保存门店、门店图片'''
    urls = []
    for item in img_files:
        ret, url = qiniu_upload(item, 'shop')
        if ret:
            urls.append(url)

    try:
        with transaction.atomic():
            shop.save()

            now = datetime.now()
            user_id = shop.updatedUser
            shopImgs = [ShopImg(shop=shop, imgUrl=url, status=0,
                                createdTime=now, createdUser=user_id, updatedTime=now,
                                updatedUser=user_id) for url in urls]
            ShopImg.objects.bulk_create(shopImgs)
            return True
    except Exception as e:
        return False
