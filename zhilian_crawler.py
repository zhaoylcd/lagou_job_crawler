#-*- coding:utf-8 -*-
__author__ = 'liang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('../')

import cookielib
from crawler import *
from common import webutil
import zhilian_crawler_data
import config
from lxml import etree

class zhilian_crawler(crawler):
    def crawler(self, key_words = None, hy = None, city = None):
        ua = webutil.get_user_agent()
        cookieJar = cookielib.MozillaCookieJar()

        #第一步，请求首页，拿到cookie
        retry_count = 10
        while True:
            try:
                html_src = webutil.request(zhilian_crawler_data.first_url, headers = zhilian_crawler_data.first_url_request_header, timeout = 60, encoding = 'utf-8', proxy = None, cookie = cookieJar, ua = ua)
                if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                    raise Exception(u'下载首页太大或太小')
                break
            except Exception as e:
                print u'下载首页异常%s' % e
                retry_count -= 1
                if retry_count <= 0:
                    raise Exception(u'下次首页%s都失败，抛出异常' % retry_count)
                time.sleep(10)
                continue

        search_url = zhilian_crawler_data.get_search_url(key_words, hy, city, page_num = 1)
        #第二步，根据关键字搜索
        while True:
            try:
                html_src = self.get_result_page_by_page_num(search_url, cookieJar, ua)
                search_url = self.get_next_page_url(html_src)
                if search_url == None:
                    break
                self.get_and_product_detail_url(html_src)
            except Exception as e:
                raise Exception(u'下载搜索首页异常%s' % e)

    def get_result_page_by_page_num(self, search_url, cookieJar = None, ua = None, proxy = None):
        search_header = zhilian_crawler_data.get_search_url_header()

        try:
            html_src = webutil.request(search_url, headers = search_header, cookie = cookieJar, ua = ua, encoding = 'utf-8', retry = 5, timeout = 60, proxy = proxy)
            if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                raise Exception(u'下载结果页太大或太小')
            return html_src
        except Exception as e:
            print u'下载结果页异常 %s' % e
            raise Exception(u'下载结果页异常')

    def get_next_page_url(self, html_src = None):
        if html_src == None or len(html_src) < 100:
            return
        try:
            tree = etree.HTML(html_src)
            page_down_xpath = tree.xpath('.//*[@class="pagesDown-pos"]/a')
            if page_down_xpath != None and len(page_down_xpath) > 0:
                next_page_url = page_down_xpath[0].get('href')
                return next_page_url
            else:
                return None
        except Exception as e:
            raise Exception(u'提取下一页链接异常%s' % e)

    def get_and_product_detail_url(self, html_src = None):
        if html_src == None or len(html_src) < 1:
            return
        try:
            tree = etree.HTML(html_src)
            a_href_list_xpath = tree.xpath('.//*[@class="zwmc"]/div/a')
            if a_href_list_xpath != None and len(a_href_list_xpath) > 0:
                [self.product(result.get('href')) for result in a_href_list_xpath]
        except Exception as e:
            raise Exception(u'获取详情页链接异常')

if __name__ == '__main__':
    zc = zhilian_crawler('zhilian','zhilian',["zhilian:detail_url"],redis_host = config.redis_host, redis_port = config.redis_port)
    zc.crawler('python','210500',u'成都')






