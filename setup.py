'''
@Author: apuyuseng
@Date: 2020-04-20 17:13:19
@LastEditTime: 2020-04-20 21:53:03
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /scrapy-proxy/setup.py
'''
import sys
from distutils.core import setup

setup(name='scrapy-proxy',
        version='0.1',
        description='Scrapy Proxy: redis pool random proxy middleware for Scrapy',
        author='apuyuseng',
        author_email='apuyuseng@gmail.com',
        url='https://github.com/apuyuseng/scrapy-proxy',
        packages=['scrapy_proxy'],
        )