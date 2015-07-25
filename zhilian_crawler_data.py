#-*- coding:utf-8 -*-
__author__ = 'liang'
import urlparse

first_url = 'http://www.zhaopin.com/'
first_url_request_header = {
    'Host': urlparse.urlparse(first_url).netloc,
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

def get_search_url(key_words = None, hy_in = None, jl = None, page_num = 1):
    base_url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?'
    # if key_words == None and hy_in == None and jl == None:
    #     return None

    base_web_forms = []
    if hy_in != None and len(hy_in) > 0:
        base_web_forms.append('in=%s' % hy_in)

    if jl != None and len(jl) > 0:
        base_web_forms.append('jl=%s' % jl)

    if key_words != None and len(key_words) > 0:
        base_web_forms.append('kw=%s' % key_words)

    if page_num >= 1:
        base_web_forms.append('p=%s' % page_num)

    if len(base_web_forms) > 0:
        web_forms = '&'.join(base_web_forms)

    if web_forms != None:
        base_url += web_forms

    return base_url

def get_search_url_header():
    header = {
        'Host': 'sou.zhaopin.com',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://sou.zhaopin.com/',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    return header

#下载详情页header
def get_detail_url_header():
    header = {
        'Host': 'jobs.zhaopin.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }

if __name__ == '__main__':
    print get_search_url('python', '210000','cd')




