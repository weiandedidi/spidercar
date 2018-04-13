# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field, Item


class SpidercarItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class TaoPageItem(Item):
    dealerId = Field()
    siteId = Field()
    pageUrl = Field()


class TaoCarItem(Item):
    trimm_name = Field()
    t_tid = Field()
    mileage = Field()
    first_license_date = Field()
    province = Field()
    city = Field()
    price = Field()
    url = Field()
    pic_url = Field()
    source_id = Field()
    dealer_id = Field()
    site_id = Field()
