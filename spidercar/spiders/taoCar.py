# -*- coding: utf-8 -*-
import json
import re
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from spidercar.items import TaoCarItem
from spidercar.spiders.utils import Mysql

pc_car_prefix = 'http://www.taoche.com/v'
pc_car_middle = '/car/?page='
pc_car = '/car/'
db = Mysql()
SOURCE_ID = 4


class TaoCarSpider(RedisSpider):
    """
    淘车的usl生成爬虫
    """
    name = "taoCar"
    allowed_domains = ["taoche.com"]
    redis_key = 'taoPages:start_urls'
    dealerDict = {}

    def __init__(self, *args, **kwargs):
        self.db = Mysql()
        dealers = self.getAllDealer()
        for dealer in dealers:
            dealerId = dealer['dealer_id']
            siteId = dealer['site_id']
            self.dealerDict[siteId] = dealerId
        super(TaoCarSpider, self).__init__(*args, **kwargs)

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
                    request = Request(link, callback=self.parseCarDetail)
                    request.meta['carUrl'] = link
                    yield request

    def parseCarDetail(self, response):
        """
        二级页面解析解析车源页
        """
        trimm_name = ''
        t_tid = 0
        mileage = 0
        first_license_date = ''
        province = ''
        city = ''
        price = 0
        pic_url = ''
        site_id = 0
        dealer_id = 0

        # 解析list页面获取car的link
        html = response.body
        # 解析
        soup = BeautifulSoup(html, 'lxml')
        h2_name = soup.find('h2', {'class': 'd-tle'})
        if None != h2_name:
            trimm_name = h2_name.text.strip().encode('gbk', 'ignore')

        price_tag = soup.find('input', id='hidCarPrice')
        if None != price_tag:
            price = price_tag['value']

        tid_tag = soup.find('input', id='hidCarID')
        if None != tid_tag:
            tid = tid_tag['value']

        first_license_date_tag = soup.find('input', id='hidBuyCarDate')
        if None != first_license_date_tag:
            first_license_date = first_license_date_tag['value']

        mileage_tag = soup.find('input', id='hidDMileage')
        if None != mileage_tag:
            mileage = mileage_tag['value']

        site_tag = soup.find('input', id='hiddvaid')
        if None != site_tag:
            site_id = site_tag['value']
            dealer_id = self.dealerDict[site_id]

        location = soup.find('meta', {'name': 'location'})
        if None != location:
            content = location['content']
            # 分割字符串
            address_list = re.split('[=;]', content)
            province = address_list[1].strip().encode('gbk', 'ignore')
            city = address_list[3].strip().encode('gbk', 'ignore')
        # url
        imgs = soup.find_all('img', {'class': 'swiper-lazy'})
        pic_dic = {}
        if len(imgs) > 0:
            index = 0
            for img in imgs:
                index += 1
                link_img = img['data-original']
                pic_dic[index] = link_img
            pic_url = json.dumps(pic_dic)
        item = TaoCarItem()
        item['trimm_name'] = trimm_name
        item['t_tid'] = t_tid
        item['mileage'] = mileage
        item['first_license_date'] = first_license_date
        item['province'] = province
        item['city'] = city
        item['price'] = price
        item['url'] = response.meta['carUrl']
        item['pic_url'] = pic_url
        item['source_id'] = SOURCE_ID
        item['dealer_id'] = dealer_id
        item['site_id'] = site_id
        yield item

    def getAllDealer(self):
        """
        获取待抓取车源的商家
        :return:商家id的list
        """
        sql = 'SELECT site_id,dealer_id FROM sync_car_dealer WHERE source_id =4'
        dealers = db.getAll(sql)
        self.db.dispose()
        return dealers
