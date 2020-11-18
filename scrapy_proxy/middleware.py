'''
@Author: your name
@Date: 2020-04-20 22:07:41
@LastEditTime: 2020-05-17 11:47:00
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /scrapy-proxy/redisMd.py
'''
import re
import time
import random
import base64
from json import loads
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.utils.python import global_object_name
from scrapy.http import Request, Response

# pip3 install redis
from redis import ConnectionPool, StrictRedis
import logging

log = logging.getLogger('scrapy.proxy')


class RedisMiddleware(object):
    '''
    支持http/https两种方式代理
    '''
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        # 设置redis连接代理池
        pool = ConnectionPool(**settings.get('REDIS'))
        self.redis_conn = lambda: StrictRedis(connection_pool=pool)
        self.RIDES_PROXYS_KEY = settings.get('RIDES_PROXYS_KEY')
        self.INVALID_PROXY = []

        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x)
                                    for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    @property
    def proxy(self):
        return self.get_proxy()

    def get_proxy(self, request=None):
        '''
        更换代理，并记录无效代理，避免再次使用。
        '''
        if request and request.meta.get('invalid_proxy'):
            self.INVALID_PROXY.append(request.meta.get('invalid_proxy'))

        conn = self.redis_conn()
        proxy_count = conn.llen(self.RIDES_PROXYS_KEY)
        proxys = conn.lrange(self.RIDES_PROXYS_KEY,0,-1)

        log.debug('代理池中有可用ip %s个', len(proxys))
        if len(proxys)==0:
            time.sleep(3)
            return self.get_proxy()

        proxy = None
        for row in proxys:
            proxy = loads(row)
            if proxy['ip'] not in self.INVALID_PROXY:
                break
            else:
                proxy = None
        
        if not proxy:
            return self.get_proxy()

        else:
            return proxy

    def _add_proxy(self, request):
        proxy = self.proxy
        if proxy:
            link = request._get_url()
            http_type = link.split('://')[0]
            proxy_url = '{http_type}://{ip}'.format(
                    http_type=http_type, **proxy)
            if proxy.get('account') and proxy.get('password'):
                auth = "Basic %s" % (base64.b64encode(
                    ('{account}:{password}'.format(**proxy)).encode('utf-8'))).decode('utf-8')
                request.headers['Proxy-Authorization'] = auth
            request.meta['proxy'] = proxy_url  # 设置代理
            request.meta['proxy_details'] = proxy
            log.debug("%s using proxy: %s" %
                      (request._get_url(), request.meta['proxy']))

    def process_request(self, request, spider):
        '''
        连接请求会先到这里，在这里进行代理设置、以及伪装等工作
        '''
        # 采用gzip压缩加速访问
        # request.headers.setdefault('Accept-Encoding','gzip')
        log.info('req')
        # 指定了ip,将不进行处理
        if 'proxy' in request.meta:
            return

        if request.meta.get('invalid_proxy'):
            self.INVALID_PROXY.append(request.meta.get('invalid_proxy'))
        self._add_proxy(request)

    def process_response(self, request, response, spider):
        '''
        因为不同的网站，封ip后的提升不一样，所以调用spider check_hander_close_ip
        来处理是否继续，这样可以自定义处理。
        '''
        log.debug(request._get_url())
        if hasattr(spider, 'check_invalid_proxy'):
            res = spider.check_invalid_proxy(response, request)
            if isinstance(res, Request) and request.meta.get('proxy'):
                res.meta['invalid_proxy'] = request.meta.get(
                    'proxy').split(':', 1)[-1].split('@')[-1]
            return res
        return response

    # def process_exception(self, request, exception, spider):
    #     spider.logger.error('代理插件报错了 %s', exception)
    #     if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
    #             and not request.meta.get('dont_retry', False):
    #             # 代理超时，标记不能使用
    #         self.INVALID_PROXY.append(request.meta.get(
    #             request.meta.get('proxy').split(':', 1)[-1].split('@')[-1]))
    #         self._add_proxy(request)
