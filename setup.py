'''
@Author: apuyuseng
@Date: 2020-04-20 17:13:19
@LastEditTime: 2020-05-02 12:30:21
@LastEditors: Please set LastEditors
@Description: In User Settings Edit
@FilePath: /scrapy-proxy/setup.py
'''
import sys
from distutils.core import setup

setup(name='scrapy-proxy',
        version='0.2',
        description='Scrapy Proxy: 从redis 中随机获取代理',
        author='apuyuseng',
        author_email='apuyuseng@gmail.com',
        url='https://github.com/apuyuseng/scrapy-proxy',
        packages=['scrapy_proxy'],
        install_requires=['redis',],
        )