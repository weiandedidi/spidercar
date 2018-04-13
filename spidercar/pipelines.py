# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import pymysql

from spidercar.items import TaoCarItem
from spiders.utils.mysqlutil import Mysql


class SpidercarPipeline(object):
    # 可以写入队列 也可以用全局变量存着，达到多少条提交
    def __init__(self):
        # 初始链接数据库
        self.db = Mysql()
        self.carItems = []

    def process_item(self, item, spider):
        if isinstance(item, TaoCarItem):
            self.process_car_item(item)
        return item

    def process_tao_item(self, item):
        """
        保存车源，超过1000条存入数据库
        """
        sql = 'INSERT INTO sync_car(trimm_name,t_tid, mileage, first_license_date, province, city, price, url, pic_url, source_id, dealer_id,site_id)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        trimm_name = item['trimm_name']
        t_tid = item['t_tid']
        mileage = item['mileage']
        first_license_date = item['first_license_date']
        province = item['province']
        city = item['city']
        price = item['price']
        url = item['url']
        pic_url = item['pic_url']
        source_id = item['source_id']
        dealer_id = item['dealer_id']
        site_id = item['site_id']
        dealer = (
            trimm_name, t_tid, mileage, first_license_date, province, city, price, url, pic_url, source_id, dealer_id,
            site_id
        )
        self.carItems.append(dealer)
        if len(self.carItems) > 1:
            try:
                self.db.batchInsert(sql, self.carItems)
                # 清空
                self.carItems = []
            except pymysql.Error, e:
                logging.error(e.message)
