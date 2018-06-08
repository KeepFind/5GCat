import socket
import hmac
from hashlib import sha1
import base64

import six


def parseURL(url):
    '''解析URL'''
    iplist = socket.gethostbyname_ex(url)
    if len(iplist) == 0:
        return None
    ips = iplist[2]
    if len(ips) == 0:
        return None
    return ips[0]


def calSignature(signString, sk):
    '''认证签名'''
    # if isinstance(sk, six.text_type):
    sk = sk.encode(encoding='utf-8')
    signString = signString.encode(encoding='utf-8')

    mac = hmac.new(sk, signString, sha1)
    return base64.b64encode(mac.digest())
