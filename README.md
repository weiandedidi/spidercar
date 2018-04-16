# 二手车分布式爬虫
## scrapy_redis 架构
## 注意事项：
### 1. 解析html文件的时候，注意编码，scrapy框架存入item中，是以json存入的，gbk形式的编码，会报错
`UnicodeDecodeError: 'utf8' codec can't decode byte 0xba in position 0: inval`