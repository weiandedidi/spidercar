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
    dealerId = Field()
    siteId = Field()
    carUrl = Field()
