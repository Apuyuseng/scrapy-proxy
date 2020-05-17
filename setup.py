'''
@Author: apuyuseng
@Date: 2020-04-20 17:13:19
@LastEditTime: 2020-05-17 16:24:29
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /scrapy-proxy/setup.py
'''
import sys
from distutils.core import setup

setup(name='scrapy-proxy',
        version='0.3',
        description='Scrapy Proxy: 从redis 中随机获取代理',
        author='apuyuseng',
        author_email='apuyuseng@gmail.com',
        url='https://github.com/apuyuseng/scrapy-proxy',
        packages=['scrapy_proxy'],
        install_requires=['redis',],
        )