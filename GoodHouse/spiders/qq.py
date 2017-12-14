import re
import time
import json
from math import ceil

from scrapy import Spider, Request
from selenium import webdriver

from GoodHouse.utils.f import find, house_type_split
from GoodHouse.xpath import qq as q
from GoodHouse.settings import CITY, KW_DICT


class QQ(Spider):

    name = 'qq'

    custom_settings = {
        'GoodHouse.middlewares.ua.RandomUserAgent': None,
    }

    start_urls = [
        'http://db.house.qq.com/xian',
    ]

    driver = webdriver.Chrome()
    driver.set_page_load_timeout(3)

    def start_requests(self):
        for url in self.start_urls:
            self.driver_get(url)
            total_count = self.driver.find_element('search_result_num').text
            city = url.split('/')[-1]
            for _ in range(int(int(total_count) / 10)):
                try:
                    for house in self.driver.find_elements_by_xpath(q.IDS):
                        house_id = house.get_attribute('data-hid')
                        link = url + '_' + house_id + '/'
                        # # 首页
                        # yield Request(
                        #     url=link,
                        #     callback=self.parse_shouye,
                        #     meta={'house_id': house_id, 'city': city}
                        # )
                        # 详情
                        yield Request(
                            url=link + 'info.html',
                            callback=self.parse_xiangqing,
                            meta={'house_id': house_id, 'city': city}
                        )
                        # 相册
                        yield Request(
                            url=link.replace('db', 'photo') + 'photo/',
                            callback=self.parse_xiangce,
                            meta={'house_id': house_id}
                        )
                except:
                    self.logger.warning('houses unreachable %s',
                                        self.driver.current_url)
                try:
                    self.driver.find_element_by_xpath(q.NEXT_PAGE).click()
                    time.sleep(1)
                except:
                    self.logger.warning('next page unreachable %s',
                                        self.driver.current_url)

    def driver_get(self, url):
        try:
            self.driver.get(url)
        except:
            self.driver.execute_script('window.stop();')

    # def parse_shouye(self, response):
    #     pass

    def parse_xiangqing(self, response):
        house = {
            'table': self.name,
            'house_id': response.meta['house_id'],
            'city': CITY[response.meta['city']]
        }
        items = response.xpath(q.BASIC)
        if not items:
            self.logger.warning('basic items unreachable %', response.url)
        else:
            for item in items:
                name = find(item, './span/text()')
                if not name:
                    continue
                if name not in KW_DICT:
                    self.logger.warning('! name %s %s', name, response.url)
                    continue
                house[KW_DICT[name]] = find(item, './p/text()')

        jtpt = find(response, q.JTPT, False)
        if not jtpt:
            self.logger.warning('unreachable jtpt %s', response.url)
        else:
            for item in jtpt:
                if not item:
                    continue
                name, value = item.split('：', 1)
                if name not in KW_DICT:
                    self.logger.warning('! name %s %s', name, response.url)
                    continue
                house[KW_DICT[name]] = value

        yield house

    def parse_xiangce(self, response):
        pass