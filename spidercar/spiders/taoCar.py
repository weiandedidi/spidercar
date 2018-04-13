# -*- coding: utf-8 -*-
import re
import scrapy
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from spidercar.items import TaoPageItem
from spidercar.tools.mysqlutil import Mysql

pc_car_prefix = 'http://www.taoche.com/v'
pc_car_middle = '/car/?page='
pc_car = '/car/'
db = Mysql()


class TaoCarSpider(RedisSpider):
    """
    淘车的usl生成爬虫
    """
    name = "taoCar"
    allowed_domains = ["taoche.com"]
    redis_key = 'taoPages:start_urls'
    db = Mysql()

    def parse(self, response):
        linkSet = set()
        html = response.body
        soup = BeautifulSoup(html, 'lxml')
        div_car_list = soup.find('div', {'class': 'car_list'})
        aList = 0
        if None != div_car_list:
            aList = div_car_list.find_all('a')
        if aList > 0:
            for e in aList:
                link = e['href']
                if None != link and '' != link:
                    pattern = 'http://www.taoche.com/'
                    link = re.sub(pattern, 'http://m.taoche.com/', link)
                    yield Request(link, callback=self.parseCarDetail)

    def parseCarDetail(self, response):
        """
        二级页面解析解析车源页
        """
        html = response.body



    def getAllDealer():
        """
        获取待抓取车源的商家
        :return:商家id的list
        """
        sql = 'SELECT site_id,dealer_id FROM sync_car_dealer WHERE source_id =4'
        dealers = db.getAll(sql)
        return dealers
