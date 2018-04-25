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

db = Mysql()

