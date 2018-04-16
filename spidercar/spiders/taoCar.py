#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from scrapy import Request

from scrapy_redis.spiders import RedisSpider
from spidercar.items import TaoCarItem
from spidercar.spiders.utils.mysqlutil import Mysql

pc_car_prefix = 'http://www.taoche.com/v'
pc_car_middle = '/car/?page='
pc_car = '/car/'
db = Mysql()
SOURCE_ID = 4
headers_pc = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Accept-Language': 'zh-CN', 'Connection': 'keep-alive',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Host': 'www.taoche.com'}


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
            self.dealerDict[siteId] = dealer
        super(TaoCarSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        linkSet = set()
        # 转码
        context = re.search('charset=\S*', response.headers['Content-Type'])
        charset = context.group(0)
        charset = charset.replace("charset=", '')
        html = response.body.decode(charset, errors='ignore')
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
                    pcUrl = link
                    link = re.sub(pattern, 'http://m.taoche.com/', link)
                    request = Request(link, callback=self.parseCarDetail)
                    request.meta['carUrl'] = link
                    request.meta['pcUrl'] = pcUrl

                    yield request

    def parseCarDetail(self, response):
        """
        二级页面解析解析车源页
        """
        trimm_name = ''
        mileage = 0
        first_license_date = ''
        province = ''
        city = ''
        price = 0
        pic_url = ''
        site_id = -1
        dealer_id = -1
        t_brand_id = -1
        t_model_id = -1
        t_trimm_id = -1
        phone = ''

        # 解析list页面获取car的link
        # 转码
        context = re.search('charset=\S*', response.headers['Content-Type'])
        charset = context.group(0)
        charset = charset.replace("charset=", '')
        html = response.body.decode(charset)
        # 解析
        soup = BeautifulSoup(html, 'lxml')
        pcUrl = response.meta['pcUrl']
        h2_name = soup.find('h2', {'class': 'd-tle'})
        if None != h2_name:
            trimm_name = h2_name.text.strip()

        price_tag = soup.find('input', id='hidCarPrice')
        if None != price_tag:
            price = price_tag['value']

        trimm_id_tag = soup.find('input', id='hidCarID')
        if None != trimm_id_tag:
            t_trimm_id = trimm_id_tag['value']

        model_tag = soup.find('input', id='hidSerialId')
        if None != model_tag:
            t_model_id = model_tag['value']

        brand_tage = soup.find('input', id='hidBrandId')
        if None != brand_tage:
            t_brand_id = brand_tage['value']

        first_license_date_tag = soup.find('input', id='hidBuyCarDate')
        if None != first_license_date_tag:
            first_license_date = first_license_date_tag['value']

        mileage_tag = soup.find('input', id='hidDMileage')
        if None != mileage_tag:
            mileage = mileage_tag['value']

        site_tag = soup.find('input', id='hiddvaid')
        if None != site_tag:
            site_id = int(site_tag['value'])
            dealer = self.dealerDict[int(site_id)]
            dealer_id = dealer['dealer_id']
            phone = dealer['phone']

        # 通过pc端进行取位置
        pc_r = requests.get(url=pcUrl, headers=headers_pc)
        # 转码
        pcContext = re.search('charset=\S*', pc_r.headers['Content-Type'])
        pcCharset = pcContext.group(0)
        pcCharset = charset.replace("charset=", '')
        pc_html = pc_r.text.decode(pcCharset, 'ignore')
        pcSoup = BeautifulSoup(pc_html, 'lxml')
        location = pcSoup.find('meta', {'name': 'location'})
        if None != location:
            content = location['content']
            # 分割字符串
            address_list = re.split('[=;]', content)
            province = address_list[1].strip()
            city = address_list[3].strip()
        if '' == city or '' == province:
            return
            # url
        imgs = soup.find_all('img', {'class': 'swiper-lazy'})
        pic_url = ''
        if len(imgs) > 0:
            index = 0
            for img in imgs:
                index += 1
                link_img = img['data-original']
                pic_url = pic_url + '|' + link_img
            # 截取的到1到最后一位，去掉首位的|
            pic_url = pic_url[1:len(pic_url)]
        item = TaoCarItem()
        item['trimm_name'] = trimm_name
        item['t_brand_id'] = t_brand_id
        item['t_model_id'] = t_model_id
        item['t_trimm_id'] = t_trimm_id
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
        item['phone'] = phone
        create_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['create_datetime'] = create_datetime
        yield item

    def getAllDealer(self):
        """
        获取待抓取车源的商家
        :return:商家id的list
        """
        sql = 'SELECT site_id,dealer_id,phone FROM sync_car_dealer WHERE source_id =4'
        dealers = db.getAll(sql)
        self.db.dispose()
        return dealers
