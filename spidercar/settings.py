# Scrapy settings for example project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
SPIDER_MODULES = ['spidercar.spiders']
NEWSPIDER_MODULE = 'spidercar.spiders'

USER_AGENT = 'scrapy-redis (+https://github.com/rolando/scrapy-redis)'

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

ITEM_PIPELINES = {
    'spidercar.pipelines.SpidercarPipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 400,
}

LOG_LEVEL = 'DEBUG'

REDIS_HOST = '10.18.37.17'

REDIS_PORT = 6379
# REDIS_URL = 'redis://user:passpord@hostname:port/db'
REDIS_URL = 'redis://:maqidi4915338@10.18.34.17:6379/0'

REDIS_PARAMS  = {'password': 'maqidi4915338'}

MYSQL_HOST = '10.11.172.233'
MYSQL_PORT = 3306
MYSQL_USER = 'wanjiang'
MYSQL_PWD = 'wanjiang0310'
MYSQL_NAME = 'hahah'
MYSQL_CHAR = 'gbk'

# Introduce an artifical delay to make use of parallelism. to speed up the
# crawl.
DOWNLOAD_DELAY = 1
