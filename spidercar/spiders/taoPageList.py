#!/usr/bin/python 
# -*- coding: UTF-8 -*-
""" 
@version: v1.0 
@author: qidima 
@license: Apache Licence  
@contact: weiandedidi@qq.com 
@site:  
@software: PyCharm 
@file: taoPageList.py 
@time: 2018/4/12 19:24 
"""
import logging

import os
import redis
import requests
import sys
from bs4 import BeautifulSoup

# 根路径拓展
sys.path.append("../../")
# 查看python的包查找路径
# print(os.sys.path)
from utils.mysqlutil import Mysql

pc_car_prefix = 'http://www.taoche.com/v'
pc_car_middle = '/car/?page='
pc_car = '/car/'
db = Mysql()
r = redis.from_url('redis://:maqidi4915338@10.18.34.17:6379/0')

# 设置日志
logging.basicConfig(level=logging.INFO,
                    filename='/root/maqidi/script/log/log.txt',
                    filemode='w',
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

headers_pc = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Accept-Language': 'zh-CN', 'Connection': 'keep-alive',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Host': 'www.taoche.com'}


def getAllDealer():
    """
    获取待抓取车源的商家
    :return:商家id的list
    """
    sql = 'SELECT site_id,dealer_id FROM sync_car_dealer WHERE source_id =4'
    dealers = db.getAll(sql)
    db.dispose()
    return dealers


def generatePageList(dealers):
    start_urls = 'taoPages'
    try:
        for dealer in dealers:
            siteId = dealer['site_id']
            dealerUrl = pc_car_prefix + str(siteId) + pc_car
            total = getPageNum(dealerUrl)
            for i in (1, total + 1):
                pageUrl = pc_car_prefix + str(siteId) + pc_car_middle + str(i)
                r.sadd(start_urls, pageUrl)
    except UnicodeEncodeError, e:
        logging.error(e.message)
    except Exception, e:
        logging.error(e.message)
    finally:
        pass


def getPageNum(url):
    """
    获取所有的商家列表页，返回列表页的数
    :param url: url
    :return:商家列表页的最大页数
    """
    r = requests.get(url=url, headers=headers_pc)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    page_box = soup.find('div', {'class': 'pag_box'})
    total = 1
    if None != page_box:
        pages = page_box.findAll('a')
        if len(pages) > 2:
            total = int(pages[-2].text)
    # 一页数据的没有下一页
    return total


if __name__ == '__main__':
    dealers = getAllDealer()
    generatePageList(dealers)
