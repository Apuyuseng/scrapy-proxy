<!--
 * @Author: apuyuseng
 * @Date: 2020-04-26 16:23:54
 * @LastEditTime: 2020-05-02 12:31:18
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /scrapy-proxy/readme.md
 -->
## scrapy_proxy

### 安装

`python3 setup.py install`

或者

`pip3 install git+https://github.com/Apuyuseng/scrapy-proxy.git`

### 启用插件

settings.py 
```python

SPIDER_MIDDLEWARES = {
    "scrapy_proxy.RedisMiddleware": 400
}

# 配置redis
RIDES = {
    # 还可以填相关参数，和redis.ConnectionPool参数一致
    'host':'localhost'
}

# 这里填写redis中存储等代理key,代理存储方式应该是列表，其中列表元素是json形式,如{'ip':'xxx.xxx.xxx.xxx:8080',account:'', 'password':''}
RIDES_PROXYS_KEY = ''
```

### 检测ip被封

有些网站在检测到爬虫后会采取封ip,但是状态码是正常的，所以插件在每次请求返回数据都会调用 `spider.check_invalid_proxy(response, request)`, 如果检测不正常可以进行一定处理，然后返回request对象，插件将会更换代理
