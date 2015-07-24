#-*- coding:utf-8 -*-
__author__ = 'liang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('../')
import time
import urllib
import cookielib
import json

from crawler import *
from common import webutil
import lagou_crawler_data
from lxml import etree
import config

class lagou_crawler(crawler):
    def crawler(self, key_words = None, hy = None, city = None):
        ua = webutil.get_user_agent()
        cookieJar = cookielib.MozillaCookieJar()

        #第一步，请求拉勾网首页，获取cookie
        retry_count = 10
        while True:
            try:
                html_src = webutil.request(lagou_crawler_data.lagou_url, headers = lagou_crawler_data.get_lagou_header(), timeout = 60, encoding = 'utf-8', cookie = cookieJar, ua = ua)
                if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                    raise Exception(u'请求的页面太大或太小，异常')
                break
            except Exception as e:
                print u'获取首页异常%s' % e
                retry_count -= 1
                if retry_count > 0:
                    time.sleep(5)
                    continue
                raise Exception(u'获取首页异常，需要加换代理或其它手段')


        #第二步，提交查询请求

        search_url, query_data = lagou_crawler_data.get_lagou_search_url(key_words, hy, city)
        if search_url == None:
            raise Exception(u'搜索关键字为空，异常')

        try:
            html_src = webutil.request(search_url, headers = lagou_crawler_data.get_lagou_search_header(), data = query_data, cookie = cookieJar, ua = ua, proxy = None, encoding = 'utf-8', retry = 5, timeout = 60)
            if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                raise Exception(u'搜索%s异常' % search_url)
        except Exception as e:
            print u'下载搜索首页异常 %s' % e
            raise Exception(u'下载搜索首页异常')

        #第三步，提取post请求，查询具体数据
        #提取第一页查询结果
        post_data = lagou_crawler_data.get_lagou_position_post_data(first = 'true', keyword = key_words, page_num = 1)

        position_id_list = []
        try:
            html_src = self.get_result_page(search_url, hy, city, post_data, cookieJar, ua, proxy = None)
            data_dict = self.json_to_dict(html_src)
            if "success" in data_dict:
                if data_dict["success"] != "true" and data_dict["success"] != True:
                    return

            if "content" in data_dict:
                content = data_dict["content"]
                total_page_count = content["totalPageCount"]
                if int(total_page_count) == 0:
                    return

                seach_results = content["result"]
                if seach_results != None and len(seach_results) > 0:
                    [self.product(str(result['positionId'])) for result in seach_results]
                    position_id_list.extend([result['positionId'] for result in seach_results])
        except Exception as e:
            print u'请求结果首页异常%s' % e
            raise Exception(u"请求结果首页异常")

        if total_page_count != None and total_page_count > 1:
            post_data['first'] = 'false'
            for i in xrange(2, total_page_count):
                post_data['pn'] = i
                try:
                    html_src = self.get_result_page(search_url, hy, city, post_data, cookieJar, ua, proxy = None)
                    data_dict = self.json_to_dict(html_src)
                    if "content" in data_dict:
                        content = data_dict["content"]
                        seach_results = content["result"]
                        if seach_results != None and len(seach_results) > 0:
                            [self.product(str(result['positionId'])) for result in seach_results]
                            position_id_list.extend([result['positionId'] for result in seach_results])
                            # for result in seach_results:
                            #     position_id = result['positionId']
                            #     print position_id
                except Exception as e:
                    print u'请求结果页异常'
                    time.sleep(2)
                    continue

    def get_result_page(self, search_url, hy = None, city = None, post_data = {}, cookieJar = None, ua = None, proxy = None):
         try:
            html_src = webutil.request(lagou_crawler_data.get_lagou_position_ajax_url(hy, city), headers = lagou_crawler_data.get_lagou_position_ajax_header(search_url),
                                       data = post_data, encoding = "utf-8", timeout = 60, retry = 5, cookie = cookieJar, method = webutil.POST, ua = ua, proxy = proxy)
            if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                raise Exception(u'请求结果首页内容太大或太小')
            return html_src
         except Exception as e:
            print u'请求结果首页异常%s' % e
            raise Exception(u'下载结果首页异常')

if __name__ == '__main__':
    # data = {'key_words':u'后端开发','city':u'成都'}
    # lc = lagou_crawler(**data)
    # lc.crawler()

    c = lagou_crawler('lagou','lagou',["lagou:detail_url"], redis_host = config.redis_host, redis_port = config.redis_port)
    c.process()


