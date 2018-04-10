"""
获取安居客所有新房数据
created at 2017.12.4 by broholens
"""

import re
import json
from scrapy import Spider, Request
from GoodHouse.utils.useful_functions import find
from GoodHouse.utils.useful_functions import house_type_split
from GoodHouse.xpath import anjuke as ajk_xp
from GoodHouse.settings import CITY
from GoodHouse.settings import base_info_dict
from GoodHouse.settings import room_details_dict
from GoodHouse.settings import room_price_dict


class Anjuke(Spider):
    """
    获取指定城市安居客新房数据
    """
    name = 'anjuke'

    start_urls = [
        'https://xa.fang.anjuke.com/',
        'https://bj.fang.anjuke.com/',
        'https://hz.fang.anjuke.com/',
        'https://sz.fang.anjuke.com/',
        'https://gz.fang.anjuke.com/',
        'https://sh.fang.anjuke.com/',
    ]
    # 图片链接
    ptn_pic_loc = re.compile('imageAlbumData=(.*?),];')

    def parse(self, response):
        # 获取总页数并逐一遍历
        pages = find(response, ajk_xp.TOTAL_PAGES)
        if not pages:
            self.logger.error('cannot find pages of %s', response.url)
            return
        # 每页有50条数据
        pages = int(pages) // 50 + 1

        for page in range(1, pages + 1):
            url = response.url.rstrip('/') + f'/loupan/all/p{page}/'
            yield Request(url, callback=self.parse_house_link)

    def parse_house_link(self, response):
        # 获取每页所有房源链接并逐一遍历
        house_links = find(response, ajk_xp.HOUSE_LINKS, False)
        if not house_links:
            self.logger.error('cannot find house link of %s', response.url)
            return
        for house_link in house_links:
            house_id = house_link.rstrip('/').split('/')[-1].split('.')[0]
            city = house_link.split('.')[0].split('/')[-1]
            host = house_link.split(house_id)[0]
            url = host + f'canshu-{house_id}.html'
            # 基本参数
            yield Request(url,
                          callback=self.parse_house,
                          meta={
                              'house_id': house_id,
                              'city': CITY[city]
                          })

            # 户型
            yield Request(url.replace('canshu', 'huxing'),
                          callback=self.parse_room_count)

            # 图片
            yield Request(url.replace('canshu', 'xiangce'),
                          callback=self.parse_pic,
                          meta={'house_id': house_id})

    def parse_house(self, response):
        # 解析房源的基本参数
        house = {
            'sale_status': find(response, ajk_xp.SALE_STATUS),
            'house_id': response.meta['house_id'],
            'city': response.meta['city'],
            'table': self.name
        }
        # 参数
        for item in response.xpath(ajk_xp.ITEMS):
            name = find(item, ajk_xp.NAME)
            if not name or name in ['楼盘图片', '售楼处电话']:
                continue
            if name not in base_info_dict:
                self.logger.warning('name %s unknown %s', name, response.url)
                continue
            if name in ['楼盘名称', '开发商', '物业公司']:
                value = find(item, './/a/text()') \
                        or find(item, './div[2]/text()')
            elif name in ['楼盘特点', '楼盘户型']:
                value = find(item, './/a/text()', False)
                if name == '楼盘户型':
                    value = house_type_split(value)
            elif name in ['区域位置', '参考单价']:
                value = ''.join(find(item, './/text()', False)).strip()
                value = value.lstrip(name).rstrip('[价格走势]').strip()
            else:
                value = find(item, './div[contains(@class, "des")]/text()')
            house[base_info_dict[name]] = value

        yield house

    def parse_pic(self, response):
        # 解析图片参数
        labels = find(response, ajk_xp.PIC_HEADER, False)
        if '画报' in labels:
            labels.remove('画报')
            urls = find(response, ajk_xp.PICTORIAL, False)
            for url in urls:
                yield Request(url.split('?')[0],
                              callback=self.parse_pictorial,
                              meta={'house_id': response.meta['house_id']})

        html = ''.join(response.text.replace('\n', '').split(' '))
        data = self.ptn_pic_loc.findall(html)
        if not data:
            self.logger.error('picture info not found %s', response.url)
            return

        data = data[0].replace('big', '"big"').replace('small', '"small"')\
            .replace('image_id', '"image_id"').replace('&nbsp;', ' ')\
            .replace('image_des', '"image_des"').replace('\'', '"') + ']'

        try:
            data = json.loads(data)
        except:
            self.logger.error('json loads error %s', response.url)
            return

        yield {
            'house_id': response.meta['house_id'],
            'tag': 'album',
            'table': self.name,
            'album': [
                {
                    'picture_label': label,
                    'picture_url': url,
                    'picture_description': des
                }
                for label, pic in zip(labels, data)
                for url, des in zip(pic['big'], pic['image_des'])
            ]
        }

    def parse_pictorial(self, response):
        # 画报与图片不同
        pic_items = response.xpath(ajk_xp.PIC_ITEMS)
        if not pic_items:
            self.logger.warning('pictorial is empty %s', response.url)
            return

        yield {
            'house_id': response.meta['house_id'],
            'tag': 'pictorial',
            'table': self.name,
            'pictorial': [
                {
                    'picture_url': find(item, './/img/@data-src'),
                    'picture_title': find(item, './/h3/text()'),
                    'picture_description': find(item, './/p/text()')
                }
                for item in pic_items
            ][:-2]
        }

    def parse_room_count(self, response):
        # 根据户型总数遍历每一页
        total = find(response, ajk_xp.ROOM_COUNT)
        if not total:
            self.logger.warning('room count is empty. %s', response.url)
            return
        for page in range(1, int(total) // 8 + 1 + 1):
            url = str(response.url).replace('.html', f'/s?p={page}')
            yield Request(url, callback=self.parse_room_url)

    def parse_room_url(self, response):
        # 解析所有户型链接并逐一遍历
        urls = find(response, ajk_xp.ROOM_URLS, False)
        if not urls:
            self.logger.warning('room urls is empty. %s', response.url)
            return
        for url in urls:
            yield Request(url, callback=self.parse_room)

    def parse_room(self, response):
        # 解析户型数据
        room = {
            'house_id': response.url.split('/')[-1].split('-')[0],
            'table': self.name + '_room'
        }
        pics = response.xpath(ajk_xp.ROOM_TYPE_PICS)
        if not pics:
            self.logger.warning('room pictures is empty. %s', response.url)
        else:
            room['room_album'] = [
                {
                    'picture_title': find(item, './@data-title'),
                    'picture_url': find(item, './img/@imglazyload-src')
                }
                for item in pics
            ]

        room['room_type'] = find(response, ajk_xp.ROOM_TITLES).split(',')[0]

        labels = find(response, ajk_xp.ROOM_LABELS, False)
        if not labels:
            self.logger.warning('room labels is empty %s', response.url)
        else:
            room['room_sale_status'] = labels[0]
            room['room_labels'] = [label for label in labels[1:]]

        price = response.xpath(ajk_xp.ROOM_PRICE)
        if not price:
            self.logger.warning('room price is empty %s', response.url)
        else:
            for item in price:
                name = find(item, './/strong/text()')
                if name not in room_price_dict:
                    self.logger.warning('key %s unknown %s', name, response.url)
                    continue
                room[room_price_dict[name]] = find(item, './span/text()')

        room_details = response.xpath(ajk_xp.ROOM_DETAILS)
        if not room_details:
            self.logger.warning('room details is empty %s', response.url)
        else:
            for item in room_details:
                name = find(item, './strong/text()')
                if name not in room_details_dict:
                    self.logger.warning('key %s unknown %s', name, response.url)
                    continue
                room[room_details_dict[name]] = find(item, './span/text()')

        room_description = find(response, ajk_xp.ROOM_DESCRIPTION, False)
        if not room_description:
            self.logger.warning('room description is empty %s', response.url)
        else:
            room['room_description'] = ' '.join(room_description)

        yield room