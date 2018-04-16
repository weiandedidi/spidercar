# -*- coding: utf-8 -*-
# 根路径拓展
import sys

import os
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

sys.path.append("../../")
print(os.sys.path)
from spidercar.items import TaoDealerItem, TaoPageItem

from spidercar.spiders.utils.mysqlutil import Mysql

pc_car_prefix = 'http://www.taoche.com/v'
pc_car_middle = '/car/?page='
pc_car = '/car/'
headers_pc = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Accept-Language': 'zh-CN', 'Connection': 'keep-alive',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Host': 'www.taoche.com'}


class TaopageSpider(scrapy.Spider):
    name = "taoPage"
    allowed_domains = ["www.taoche.com"]
    start_urls = ['http://www.taoche.com/']
    db = Mysql()

    def getAllDealer(self):
        """
        获取待抓取车源的商家
        :return:商家id的list
        """
        sql = 'SELECT site_id,dealer_id FROM sync_car_dealer WHERE source_id =4'
        dealers = self.db.getAll(sql)
        self.db.dispose()
        return dealers

    def parse(self, response):
        dealers = self.getAllDealer()
        for dealer in dealers:
            siteId = dealer['site_id']
            dealerUrl = pc_car_prefix + str(siteId) + pc_car
            item = TaoDealerItem()
            item['siteId'] = siteId
            item['dealerId'] = dealer['dealer_id']
            request = Request(dealerUrl, meta={'item': item}, headers=headers_pc, callback=self.parseTotal)
            yield request

    def parseTotal(self, response):
        """
        解析商家页的数量
        """
        html = response.body
        soup = BeautifulSoup(html, 'lxml')
        page_box = soup.find('div', {'class': 'pag_box'})
        siteId = response.meta['item']['siteId']
        dealerId = response.meta['item']['dealerId']
        total = 1
        if None != page_box:
            pages = page_box.findAll('a')
            if len(pages) > 2:
                total = int(pages[-2].text)
        for i in range(1, total + 1):
            item = TaoPageItem()
            pageUrl = pc_car_prefix + str(siteId) + pc_car_middle + str(i)
            item['pageUrl'] = pageUrl
            item['siteId'] = siteId
            item['dealerId'] = dealerId
