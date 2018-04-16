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


    def process_car_item(self, item):
        """
        保存车源，超过1000条存入数据库
        """
        sql = 'INSERT INTO sync_car(trimm_name,t_brand_id,t_model_id,t_trimm_id ,mileage, first_license_date, province, city, price, url, pic_url, source_id, dealer_id,site_id,phone,create_datetime)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        trimm_name = item['trimm_name']
        t_brand_id = item['t_brand_id']
        t_model_id = item['t_model_id']
        t_trimm_id = item['t_trimm_id']
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
        phone = item['phone']
        create_datetime = item['create_datetime']
        car = (trimm_name, t_brand_id, t_model_id, t_trimm_id, mileage, first_license_date, province, city, price, url,
               pic_url, source_id,
               site_id,
               dealer_id, phone, create_datetime)
        self.carItems.append(car)
        if len(self.carItems) > 2:
            try:
                self.db.batchInsert(sql, self.carItems)
                # 清空
                self.carItems = []
            except pymysql.Error, e:
                logging.error(e.message)
