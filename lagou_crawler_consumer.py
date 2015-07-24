#-*- coding:utf-8 -*-
__author__ = 'liang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('../')
import time

from common.producer_customer import Customer
from common import webutil
from common import mongoutil
from lxml import etree
import lagou_crawler_data
import cookielib
import config

class lagou_crawler_consumer(Customer):

    def __init__(self,  name,queue_name,process_number=1,redis_host=None,redis_port=None):
        Customer.__init__(self,  name,queue_name,process_number=process_number,redis_host=redis_host,redis_port=redis_port)
        self.mongo = mongoutil.getmondbv2(config.mongo_host, config.mongo_port, config.mongo_db, config.mongo_table)

    def run(self,item):
        try:
            if item != None:
                url = lagou_crawler_data.get_jobs_url(item.strip())
                print url
                self.crawl(url)
        except Exception as e:
            print u'抓取item %s 异常 %s' % (item, e)
            raise Exception(u'抓取详细页异常')

    def crawl(self, url):
        if url == None:
            return

        ua = webutil.get_user_agent()
        cookieJar = cookielib.MozillaCookieJar()

        try:
            html_src = webutil.request(url, headers = lagou_crawler_data.get_jobs_url_header(), ua = ua, cookie = cookieJar, timeout = 60, encoding = 'utf-8', retry = 5, savefile=None)
            if len(html_src) < 100 or len(html_src) > 1024 * 1024 * 10:
                raise Exception(u'下载的页面太大或太小')
        except Exception as e:
            print u'抓取%s异常 %s' % (url, e)
            raise Exception(u'抓取数据异常')

        save_data = {}
        #使用xpath提取信息
        tree = etree.HTML(html_src)
        try:
            job_title_list = tree.xpath('.//*[@class="clearfix join_tc_icon"]/h1')
            if job_title_list != None and len(job_title_list) > 0:
                job_title = job_title_list[0].get('title')
                save_data['job_title'] = str(job_title)
            else:
                save_data['job_title'] = ''
            work_place_xpath = tree.xpath('.//*[@class="job_request"]/span[2]/text()')
            if work_place_xpath != None and len(work_place_xpath) > 0:
                work_place = work_place_xpath[0]
                save_data['work_place'] = str(work_place)
            else:
                save_data['work_place'] = ''

            publish_time_xpath = tree.xpath('.//*[@class="job_request"]/div[1]/text()')
            if publish_time_xpath != None and len(publish_time_xpath) > 0:
                publish_time = publish_time_xpath[0]
                save_data['publish_time'] = str(publish_time)
            else:
                save_data['publish_time'] = ''

            work_request_xpath = tree.xpath('.//*[@class="job_bt"]/p/text()')
            if work_request_xpath != None and len(work_request_xpath) > 0:
                work_request = work_request_xpath[0]
                save_data['work_request'] = str(work_request)
            else:
                save_data['work_request'] = ''
        except Exception as e:
            print u'解析页面异常%s' % e

        #存储数据
        try:
            self.save_data(url, save_data)
        except Exception as e:
            print u'存储数据异常%s' % e
            raise Exception(u'存储数据异常')

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
    lcc = lagou_crawler_consumer('lagou_job_consumer', 'lagou:detail_url', redis_host = config.redis_host, redis_port = config.redis_port)
    lcc.start()