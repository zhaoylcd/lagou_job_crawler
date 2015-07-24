#-*- coding:utf-8 -*-
__author__ = 'liang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pymongo
import socket
import time
import json
from abc import *
from common.producer_customer import Producer
from common import RedisQueue
class crawler(Producer):

    socket.setdefaulttimeout(60.0)

    def __init__(self, key_queue_name, name,queue_name,process_number=1,redis_host=None,redis_port=None):
        Producer.__init__(self,name, queue_name, process_number, redis_host = redis_host, redis_port = redis_port)
        self.key_queue_name = key_queue_name
        self.key_queue_conn = RedisQueue.getredisQueue("%s:keywords" % key_queue_name, redis_host = redis_host,redis_port = redis_port, redis_password = None)
        self.redis_host = redis_host
        self.redis_port = redis_port

    @abstractmethod
    def crawler(self, key_words = None, hy = None, city = None):
        pass

    def pop_key_words(self):
        while True:
            try:
                keywords_dict = self.key_queue_conn.get(timeout=60)
                if keywords_dict is None:
                    raise Exception(u'队列中没有内容返回')
                keywords_dict = keywords_dict.strip()
                if len(keywords_dict) < 1:
                    raise Exception(u'队列中数据异常')
                return keywords_dict
            except Exception as e:
                print u'从队列中%s取key,value对异常 %s' % (self.key_queue_name, e)
                time.sleep(60*5)
                try:
                    #重新连接
                    self.company_name_queue = RedisQueue.getredisQueue("%s:keywords" % self.key_queue_name,redis_host= self.redis_host,redis_port=self.redis_port)
                    continue
                except Exception as e1:
                    self.logging.error(u"连接Redis队列失败。错误信息:%s" % e1)
                    time.sleep(600)
                continue

    def json_to_dict(self, data_json = None):
        try:
            if data_json == None:
                return None
            data = json.loads(data_json)
            return data
        except Exception as e:
            print u'json convert to dict failed!'
            raise

    # def save(self, data_dict = None):
    #     pass
    def append_bottom(self, keywords_dict):
        while True:
            try:
                keywords_str = json.dumps(keywords_dict)
                self.key_queue_conn.put(keywords_str)
                return
            except Exception as e:
                print u'重新插入redis队尾异常%s' % e
                time.sleep(5)
                try:
                    #重新连接
                    self.company_name_queue = RedisQueue.getredisQueue("%s:keywords" % self.key_queue_name,redis_host= self.redis_host,redis_port=self.redis_port)
                    continue
                except Exception as e1:
                    self.logging.error(u"连接Redis队列失败。错误信息:%s" % e1)
                    time.sleep(600)
                continue

    def process(self):
        failed_count = 10
        while True:
            try:
                keywords = self.pop_key_words()
                if len(keywords) < 1:
                    raise Exception(u'搜索关键词异常')
                else:
                    keywords = self.json_to_dict(keywords)
            except Exception as e:
                print u'队列中取值错误%s' % e
                time.sleep(10)
                continue

            try:
                self.crawler(key_words = keywords['key_words'], hy = keywords['hy'], city = keywords['city'])
            except Exception as e:
                print u'抓取数据异常%s' % e
                time.sleep(10)
                failed_count -= 1
                self.append_bottom(keywords)

if __name__ == '__main__':
    pass