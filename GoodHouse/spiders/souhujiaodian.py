"""
https://xian.focus.cn/loupan/171918/xiangqing.html
created at 2017.12.4 by broholens
"""

import re
import json
from math import ceil

from scrapy import Spider, Request

from GoodHouse.utils.f import find, house_type_split
from GoodHouse.xpath import souhujiaodian as shjd_xp


class Souhujiaodian(Spider):

    name = 'souhujiaodian'

    start_urls = [
        'https://xian.focus.cn/loupan/'
    ]

    city_dict = {
        'https://xian.focus.cn/loupan/': '西安市'
    }

    def parse(self, response):
        total_count = find(response, shjd_xp.TOTAL_COUNT)
        if not total_count:
            self.logger.error('total count not clear! %s', response.url)
            return
        total_pages = int(ceil(int(total_count) / 20))
        for page in range(1, total_pages + 1):
            url = response.url + f'p{page}/'
            yield Request(url,
                          callback=self.parse_house_link,
                          meta={'host': response.url})

    def parse_house_link(self, response):
        house_ids = find(response, shjd_xp.HOUSE_IDS, False)
        if not house_ids:
            self.logger.error('house ids not clear! %s', response.url)
            return
        for house_id in house_ids:
            # 详情
            yield Request(url=response.meta['host']+house_id+'/xiangqing.html',
                          callback=self.parse_xiangqing)
            # 户型
            yield Request(url=response.meta['host']+house_id+'/huxing/',
                          callback=self.parse_huxing)
            # 相册
            yield Request(url=response.meta['host']+house_id+'/xiangce/',
                          callback=self.parse_xiangce)

    def parse_xiangqing(self, response):
        pass

    def parse_huxing(self, response):
        pass

    def parse_xiangce(self, response):
        pass