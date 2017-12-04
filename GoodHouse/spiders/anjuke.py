"""
https://xa.fang.anjuke.com
created at 2017.12.4 by broholens
"""

"""
questions:

1. 如何选择城市
2. 取上整
3. 为什么不做成链接, 让用户直接访问安居客
"""

from math import ceil

from scrapy import Spider, Request
from scrapy.loader import ItemLoader

from ..items import GoodhouseItem
from ..xpath import anjuke_xpath as ajk_xp


class Anjuke(Spider):

    name = 'anjuke'

    start_urls = [
        'https://xa.fang.anjuke.com',  # xi'an
    ]

    def parse(self, response):
        pages = response.xpath(ajk_xp.TOTAL_PAGES).extract_first()
        if not pages:
            self.logger.error('cannot find pages of %s', response.url)
            return
        pages = int(ceil(int(pages) / 50))
        # todo: first page information needs to be collected
        self.parse_house_link(response)

        for page in range(2, pages + 1):
            # rstrip('/')
            url = response.url.rstrip('/') + f'/loupan/all/p{page}'
            yield Request(url, callback=self.parse_house_link)

    def parse_house_link(self, response):
        house_links = response.xpath(ajk_xp.HOUSE_LINKS).extract()
        if not house_links:
            self.logger.error('cannot find house_link of %s', response.url)
            return
        for house_link in house_links:
            house_id = house_link.rstrip('/').split('/')[-1].split('.')[0]
            host = house_link.split(house_id)[0]
            url = host + f'loupan/canshu-{house_id}.html'
            yield Request(url, callback=self.parse_house)

    def parse_house(self, response):
        loader = ItemLoader(item=GoodhouseItem, response=response)
        telephone = '转'.join(response.xpath(ajk_xp.TELEPHONE).extract())
        loader.add_value('telephone', telephone)
