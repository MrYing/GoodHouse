# -*- coding: utf-8 -*-

# Scrapy settings for GoodHouse project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'GoodHouse'

SPIDER_MODULES = ['GoodHouse.spiders']
NEWSPIDER_MODULE = 'GoodHouse.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'GoodHouse (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     # 'GoodHouse.middlewares.GoodhouseSpiderMiddleware': 543,
#     # 'scrapy.spidermiddlewares.depth.DepthMiddleware': None
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'GoodHouse.middlewares.MyCustomDownloaderMiddleware': 543,
    'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'GoodHouse.middlewares.ua.RandomUserAgent': 1,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'GoodHouse.pipelines.GoodhousePipeline': 300,
    # 'GoodHouse.pipelines.amap.AMap': 301,
    'GoodHouse.pipelines.mongo.MongoPipeline': 800
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

MONGO_URI = 'mongodb://localhost:27017'
MONGO_DATABASE = 'houses'


AMAP_KEYS = [
    'c5c96d4b1a01d417d046703ae06d88bd',
    '1cc614cd037bd367fe86ffd0d1094540',
    'f37aa948833a47f6107650e440aee4ed',
    '3415a2784ab651a9ae0135623c84eff3',
    '5c52252dd22fdbb9c0f337488d78d3a8',
    '637ea37a488d5ada69b9add6b51ade91',
    'e1c83a76830ca6be62c67835ac12ad5c',
    '1aff8f5ae130e3703d4ba89f46c31df8',
    '1f6d0d8ea68c21088beec7e0ca5e7b1e',
    'd962e50247065e81077eb144175d5adc',
    '0cf95ad6305d15b44bbd864ffa3c824d',
    '4eb65384161342b28599bf994c1f2450',
    'efcbbb3d1a384423b547d6725699d1c4',
    '5006648b93f630a281f29e9eeaac6ab8',
    '64e49c52cf205e03b6274ac3b4f66acd',
    '0652bb3d94666a2b59223d91539e2786',
    'ba6331d8131baec23f5b0ac4062e8325',
    '3c6d6676b2c1645d430cba4b8a4db22c',
    'fc8b23e349a99289bd87d4395cf87252',
    '4dd66beef79fb206cea77d1a78ff1b7e'
]

CITY = {
    'bj': '北京市',
    'sh': '上海市',
    'hz': '杭州市',
    'sz': '深圳市',
    'gz': '广州市',
    'xa': '西安市',
    'house': '北京市',
    'xian': '西安市',
}

LOG_LEVEL = 'INFO'
