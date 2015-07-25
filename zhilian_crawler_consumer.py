#-*- coding:utf-8 -*-
__author__ = 'liang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('../')
import time
import cookielib
from common.producer_customer import Customer
from common import webutil
from common import mongoutil
from lxml import etree
import zhilian_crawler_data
import config
import zhilian_crawler_data

class zhilian_crawler_consumer(Customer):
    def __init__(self, name,queue_name,process_number=1,redis_host=None,redis_port=None):
        Customer.__init__(self,  name,queue_name,process_number=process_number,redis_host=redis_host,redis_port=redis_port)
        self.mongo = mongoutil.getmondbv2(config.mongo_host, config.mongo_port, config.mongo_db, config.mongo_table)

    def run(self,item):
        try:
            if item != None:
                self.crawl(item)
        except Exception as e:
            print u'抓取%s详情页时异常%s' (item, e)
            raise Exception(u'抓取详情页异常')

    def crawl(self, url):
        if url == None or len(url) < 1:
            return

        ua = webutil.get_user_agent()
        cookieJar = cookielib.MozillaCookieJar()

        data_dict = {}
        data_dict['type'] = 'zhilian'
        data_dict['version'] = 1
        data_dict['url'] = url

        try:
            html_src = webutil.request(url, headers = zhilian_crawler_data.get_search_url_header(), ua = ua, cookie = cookieJar, timeout = 60, retry = 5, encoding = 'utf-8', proxy = None)
            if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                raise Exception(u'下载详情页异常')
            data_dict['html'] = html_src
            self.parse_html(html_src, data_dict)
            self.save_data(url, data_dict)
        except Exception as e:
            print u'下载详情页异常%s' % e
            raise Exception(u'下载详情页异常')

    def parse_html(self, html_src, data_dic):
        try:
            tree = etree.HTML(html_src)
            job_title_xpath = tree.xpath('.//*[@class="inner-left fl"]/h1/text()')
            if job_title_xpath != None and len(job_title_xpath) > 0:
                job_title = job_title_xpath[0]
                data_dic['job_title'] = job_title

            publish_time_xpath = tree.xpath('.//*[@id="span4freshdate"]/text()')
            if publish_time_xpath != None and len(publish_time_xpath) > 0:
                publish_time = publish_time_xpath[0]
                data_dic['publish_time'] = publish_time

            work_place_xpath = tree.xpath('.//*[@class="terminal-ul clearfix"]/li[2]/strong/a/text()')
            if work_place_xpath != None and len(work_place_xpath) > 0:
                work_place = work_place_xpath[0]
                data_dic['work_place'] = work_place

            work_request_xpath = tree.xpath('.//*[@class="tab-inner-cont"]/p/text()')
            if work_request_xpath != None and len(work_request_xpath) > 0:
                work_request = ''.join(work_request_xpath)
                data_dic['work_request'] = work_request
        except Exception as e:
            print u'解析html页面异常%s' % e
            raise Exception(u'解析html页面异常')

    def save_data(self, url, data_dic):
        if data_dic == None and len(data_dic) == 0 and not isinstance(data_dic, dict):
            return
        try:
            now = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())
            if '_id' not in data_dic:
                id = mongoutil.get_id_key(url, now)
            else:
                id = data_dic['_id']
            if None in data_dic:
                del data_dic[None]
            if 'do_time' not in data_dic:
                data_dic['do_time'] = now
            if 'uptime' not in data_dic:
                data_dic['uptime'] = time.time()

            mongoutil.updatev3(self.mongo, id, data_dic)
        except Exception as e:
            print u'保存数据异常%s' % e
            raise Exception(u'保存数据异常')

if __name__ == '__main__':
    zcc = zhilian_crawler_consumer('zhilian_job_consumer', 'zhilian:detail_url', redis_host = config.redis_host, redis_port = config.redis_port)
    zcc.start()