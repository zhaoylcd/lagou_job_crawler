#-*- coding:utf-8 -*-
__author__ = 'liang'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
from common import RedisQueue
import config
queue_list = ['lagou']
encoding = 'utf-8'

def main():
    value = u'后端开发,移动互联网,成都'
    value_list = value.split(',')
    value_dict = {}
    if len(value_list) == 3:
        value_dict['key_words'] = value_list[0]
        value_dict['hy'] = value_list[1]
        value_dict['city'] = value_list[2]
    else:
        sys.exit(1)
    while True:
        try:
            value_dict_str = json.dumps(value_dict)
            queue = RedisQueue.getredisQueuev2("%s:keywords"% queue_list[0],config.redis_host,config.redis_port, redis_password = None)
            queue.insert(value_dict_str)
            break
        except Exception as e:
            print u'insert redis failed! %s' % e

if __name__ == '__main__':
    main()



