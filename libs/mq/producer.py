# encoding:utf-8
import configparser
import hashlib
import time
import requests
from mq.util import parseURL, calSignature


class HttpProducer(object):
    '''消息发布者'''

    def __init__(self):
        self.signature = "Signature"
        self.producerid = "ProducerID"
        self.topic = "Topic"  # 消息主题
        self.ak = "AccessKey"
        self.cf = configparser.ConfigParser()  # 配置文件解析器
        self.md5 = hashlib.md5()  # MD5对象

    def process(self):
        '''发布消息主流程'''

        self.cf.read("properties", encoding='utf-8')  # 读取消息主题
        topic = self.cf.get("property", "Topic")  # 存储消息URL路径
        url = self.cf.get("property", "URL")  # 访问码
        ak = self.cf.get("property", "Ak")  # 密钥
        sk = self.cf.get("property", "Sk")
        pid = self.cf.get("property", "ProducerID")  # Producer ID

        content = "中文".encode('utf-8')  # HTTP请求主体内容
        newline = "\n"  # 分隔符

        self.md5.update(content)  # 根据HTPP主体内容计算MD5值
        s = requests.Session()
        try:
            for index in range(0, 100):
                date = repr(int(time.time() * 1000))[0:13]  # 时间戳
                signString = str(topic + newline + pid + newline + self.md5.hexdigest() + newline + date)  # 构造签名字符串
                sign = calSignature(signString, sk).decode('utf-8')  # 计算签名
                contentFlag = "Content-type"  # 内容类型
                headers = {
                    self.signature: sign,
                    self.ak: ak,
                    self.producerid: pid,
                    contentFlag: "text/html;charset=UTF-8"
                }
                s.headers.update(headers)
                # 开始发送HTTP请求消息
                r = s.post(url + "/message/?topic=" + topic + "&time=" + date + "&tag=http&key=http", data=content)
                msg = r.text
                print("response:" + msg)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    producer = HttpProducer()  # 创建消息发布者
    producer.process()  # 开启消息发布者
