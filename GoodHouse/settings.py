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
MONGO_DATABASE = 'house'


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

base_info_dict = {
    # source_web
    '楼盘名称': 'building_name',
    '楼盘特点': 'feature',  # 项目特色 building_character
    '参考单价': 'price',
    '最低首付': 'minidown_payment',
    '物业类型': 'property_type',
    '物业类别': 'property_type',
    '装修状况': 'decorate_situation',
    '环线位置': 'loop_position',
    '区域位置': 'region',
    '开发商': 'developer',
    '承建商': 'developer',
    '投资商': 'developer',
    '品牌商': 'brand',
    '楼盘地址': 'building_location',
    '销售状态': 'sale_status',
    '户型': 'house_type',
    '开盘时间': 'opening_time',
    '入住时间': 'completion_time',
    # '交房时间': 'completion_time',  # 建成年代 building_time
    '价格详情': 'building_price',
    '售楼许可证': 'sales_license',
    '售楼地址': 'sale_location',
    '主力户型': 'house_type',
    '建筑类别': 'building_type',
    '交通': 'transportation',
    '轨道交通': 'transportation',
    '交通方式': 'transportation',
    '公交路线': 'bus',
    '中小学': 'school',
    '教育': 'school',
    '学校': 'school',
    '商业': 'shopping',
    '综合商场': 'shopping',
    '医院': 'hospital',
    '其他': 'entertainment',
    '建材设备': 'entertainment',
    '邮政': 'post',
    '银行': 'bank',
    '幼儿园': 'kindergarten',
    '大学': 'university',
    '供水': 'water_supply',
    '供气': 'gas_method',
    '供暖': 'hearting_supply',
    '小区内部配套': 'inner_support',
    '建筑及园林设计': 'landscape_design',
    '内部配套': 'inner_support',
    '占地面积': 'floor_area',
    '建筑面积': 'structure_area',
    '楼栋总数': 'building_num',
    '物业顾问公司': 'property_consultants',
    '物业费描述': 'property_fee_description',
    '楼栋情况': 'story_status',
    '所属商圈': 'near_business',
    '单套面积': 'single_area',
    '商业面积': 'business_area',
    '办公面积': 'office_area',
    '开间面积': 'room_area',
    '标准层高': 'standard_floor_height',
    '装修情况': 'renovation_condition',
    '装修标准': 'renovation_condition',
    '楼层说明': 'floor_description',
    '物业费': 'property_fee',
    '物业说明': 'property_fee_description',
    '供暖方式': 'heating_method',
    '水电类别': 'hydropower_category',
    '停车位配置': 'parking_count',
    '电梯配置': 'elevator',
    '嫌恶设施': 'nasty_facility',
    '所属区县': 'region',
    '项目特色': 'labels',
    '楼盘优惠': 'discount',
    '楼盘户型': 'house_type',
    '最新开盘': 'opening_time',
    '交房时间': 'completion_time',
    '建成年代': 'completion_time',
    '售楼处地址': 'sale_location',
    '预售许可证': 'license',
    '建筑类型': 'building_type',
    '产权年限': 'durable_years',
    '容积率': 'plot_ratio',
    '绿化率': 'green_rate',
    '规划户数': 'household_num',
    '总户数': 'household_num',
    '楼层状况': 'story_status',
    '工程进度': 'project_progress',
    '物业管理费': 'property_fee',
    '物业公司': 'property_company',
    '车位数': 'parking_space',
    '停车位': 'parking_space',
    '车位比': 'parking_rate',
    # business
    '总建筑面积': 'total_area',
    '招商业态': 'business_model',
    '临近商圈': 'business_district',
    '周边配套': 'business_district',
    '周边人群': 'surrounding_people',
    '出售类型': 'sale_type',
    '得房率': 'room_rate',
    '商铺总套数': 'shops_count',
    '是否统一管理': 'is_unified_management',
    '是否分割': 'is_segmentation',
    '出租类型': 'rent_type',
    '租金': 'rent',
    '是否包含物业费': 'contain_property_fee',
    '待租面积': 'for_rent_area',
    '待租套数': 'for_rent_count',
    '月供': 'month_payment',
    '楼盘总价': 'total_price',
    '标准层面积': 'standard_area',
    '公共部分精装修': 'public_exquisite',
    '临近CBD': 'cbd',
    '已签约租户': 'tenants',
    '已签约商户': 'tenants',
    # office
    '写字楼类型': 'office_building_type',
    '写字楼级别': 'office_building_level',
    '办公室面积': 'office_area',
    '招租客群': 'customer'
}

room_price_dict = {
    '参考总价:': 'reference_price',
    '参考首付:': 'reference_down_payment',
    '参考月供:': 'reference_monthly_payment'
}

room_details_dict = {
    '居  室:': 'house_type',
    '建筑面积:': 'house_area',
    '朝  向:': 'house_orientation',
    '层  高:': 'house_storey_height',
    '户型分布:': 'house_distribution'
}

LOG_LEVEL = 'DEBUG'
