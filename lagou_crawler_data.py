#-*- coding:utf-8 -*-
__author__ = 'liang'
import urllib
import urlparse

lagou_url = 'http://www.lagou.com/'

def get_lagou_header():
    header = {
        'Host': urlparse.urlparse(lagou_url).netloc,
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    return header

def get_lagou_search_url(key_words = None, hy = None, city = None):
    if key_words == None or len(key_words) < 1:
        return None, None
    search_url = 'http://www.lagou.com/jobs/'

    if "key_words" != None:
        search_url += "list_%s" % key_words
    else:
        return None, None

    query_data = {}
    #默认查找最新的
    query_data["px"] = "new"

    if hy != None and len(hy) > 1:
        query_data["hy"] = hy

    if city != None and len(city) > 1:
        query_data["city"] = city

    return search_url, query_data

def get_lagou_search_header():
    header = {
        'Host': urlparse.urlparse(lagou_url),
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }

    return header

def get_lagou_position_ajax_url(hy = None, city = None):
    base_url = 'http://www.lagou.com/jobs/positionAjax.json'
    if hy != None and len(hy) > 1:
        base_url += "?hy=%s" % hy
        base_url += "&px=new"
    else:
        base_url += "?px=new"

    if city != None and len(city) > 1:
        base_url += "&city=%s" % city

    return base_url

def get_lagou_position_ajax_header(search_url = None):
    header = {
        'Host': urlparse.urlparse(search_url).netloc,
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'http://www.lagou.com',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': search_url,
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    return header

def get_lagou_position_post_data(first = 'true', keyword = None,page_num = 1):
    if keyword == None or len(keyword) < 1:
        return None
    post_data = {
        'first':first,
        'pn':page_num,
        'kd':keyword
    }
    return post_data

def get_jobs_url(item_id = None):
    if item_id != None and len(str(item_id)) != 0:
        job_url = 'http://www.lagou.com/jobs/%s.html' % item_id
        return job_url
    else:
        return None

def get_jobs_url_header():
    header = {
        'Host': urlparse.urlparse(lagou_url).netloc,
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }

    return header