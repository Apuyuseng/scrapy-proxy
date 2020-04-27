'''
@Author: your name
@Date: 2020-04-20 22:07:41
@LastEditTime: 2020-04-27 12:37:56
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /scrapy-proxy/redisMd.py
'''
import re
import random
from scrapy.http import Request,Response
# pip3 install redis
from redis import ConnectionPool, StrictRedis
import logging

log = logging.getLogger('scrapy.proxy')


class RedisMiddleware(object):
    '''
    支持http/https两种方式代理
    原理：获取维护好到redis代理池中到代理ip
    '''
    def __init__(slef, settings):
        # 设置redis连接代理池
        pool = ConnectionPool(**settings.get('REDIS'))
        self.redis_conn = lambda : StrictRedis(connection_pool=pool)
        self.RIDES_PROXYS_KEY = settings.get('RIDES_PROXYS_KEY')
        self.INVALID_PROXY = []
       

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def change_proxy(self, request=None):
        '''
        更换代理，并记录无效代理，避免再次使用。
        '''
        if request and request.meta.get('invalid_proxy'):
           self.INVALID_PROXY.append(request.meta.get('invalid_proxy'))

        if request.meta.get('proxy','').find(self.proxy['ip'])==-1:
            # 表面代理已经被跟换了
            return

        conn = self.redis_conn()
        proxy_count = conn.llen(self.PROXY_POOL_KEY)
        log.debug('代理池中有可用ip %s个', proxy_count)
        index = random.randint(0, proxy_count)
        _proxy = conn.lindex(self.PROXY_POOL_KEY, index)
        proxy = loads(_proxy)
        # 将无效代理记录在redis中，在分布式中有一定等作用
        # res = conn.sismember(self.INVALID_PROXY_KEY, proxy['ip'])
        # if res == 0:
        #     self.proxy = proxy
        #     return proxy
        if proxy['ip'] in self.INVALID_PROXY:
            self.change_proxy(request)
        else:
            self.proxy = proxy
        



    def process_request(self, request, spider):
        '''
        连接请求会先到这里，在这里进行代理设置、以及伪装等工作
        '''
        # 采用gzip压缩加速访问
        request.headers.setdefault('Accept-Encoding','gzip')

        # 指定了ip,将不进行处理
        if 'proxy' in request.meta:
            return request

        if request.meta.get('invalid_proxy'):
            self.change_proxy(request)

        proxy = self.proxy
        proxy_url = proxy['ip']
        link = request._get_url()
        if proxy.get('account') and proxy.get('password'):
            http_type = link.split('://')[0]
            proxy_url = '{http_type}://{account}:{password}@{ip}'.format(http_type=http_type, **proxy)
            auth = "Basic %s" % (base64.b64encode(
                ('{account}:{password}'.format(**proxy)).encode('utf-8'))).decode('utf-8')
            request.headers['Proxy-Authorization'] = auth
            
        request.meta['proxy'] = proxy_url  # 设置代理
        request.meta['proxy_details'] = proxy
        log.debug("%s using proxy: %s" %
                        (request._get_url(), request.meta['proxy']))

    def process_response(self, request, response, spider):
        '''
        因为不同的网站，封ip后的提升不一样，所以调用spider check_hander_close_ip
        来处理是否继续，这样可以自定义处理。
        '''
        if hasattr(spider,'check_invalid_proxy'):
            res = spider.check_invalid_proxy(response, request)
            if isinstance(res, Request) and request.meta.get('proxy'):
                res.meta['invalid_proxy'] = request.meta.get('proxy').split(':',1)[-1].split('@')[-1]
        return response