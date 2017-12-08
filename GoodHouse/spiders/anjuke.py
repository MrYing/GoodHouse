"""
https://xa.fang.anjuke.com
created at 2017.12.4 by broholens
"""

import re
import json
from math import ceil

from scrapy import Spider, Request

from GoodHouse.utils.f import find, house_type_split
from GoodHouse.xpath import anjuke as ajk_xp


class Anjuke(Spider):

    name = 'anjuke'

    start_urls = [
        'https://xa.fang.anjuke.com',  # xi'an
    ]

    city_dict = {
        'https://xa.fang.anjuke.com/loupan/': '西安市'
    }

    kw_dict = {
        '楼盘名称': 'name',
        '楼盘特点': 'labels',
        '参考单价': 'price',
        '物业类型': 'property_type',
        '开发商': 'developer',
        '区域位置': 'region',
        '楼盘地址': 'address',
        # '售楼处电话': 'telephone',
        '最低首付': 'min_deposit',
        '楼盘优惠': 'discount',
        '楼盘户型': 'house_type',
        '最新开盘': 'opening_time',
        '交房时间': 'delivery_time',
        '售楼处地址': 'sale_address',
        '预售许可证': 'license',
        '建筑类型': 'building_type',
        '产权年限': 'durable_years',
        '容积率': 'floor_area_ratio',
        '绿化率': 'green_ratio',
        '规划户数': 'householder_count',
        '楼层状况': 'story_status',
        '工程进度': 'project_progress',
        '物业管理费': 'property_fee',
        '物业公司': 'property_company',
        '车位数': 'parking_count',
        '车位比': 'parking_ratio',
        # business
        '开间面积': 'room_area',
        '商业面积': 'business_area',
        '总建筑面积': 'total_area',
        '招商业态': 'business_model',
        '临近商圈': 'near_business',
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
        '月供': 'monthly_payment',
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

    ptn_pic_loc = re.compile('imageAlbumData=(.*?),];')
    # ptn_pic_des = re.compile('image_des:\[(.*?)]')
    # ptn_pic_url = re.compile('big:\[(.*?)]')

    def parse(self, response):
        pages = find(response, ajk_xp.TOTAL_PAGES)
        if not pages:
            self.logger.error('cannot find pages of %s', response.url)
            return
        pages = int(ceil(int(pages) / 50))
        # self.parse_house_link(response)

        for page in range(1, pages + 1):
            url = response.url.rstrip('/') + f'/loupan/all/p{page}/'
            yield Request(url, callback=self.parse_house_link)

    def parse_house_link(self, response):
        house_links = find(response, ajk_xp.HOUSE_LINKS, False)
        if not house_links:
            self.logger.error('cannot find house_link of %s', response.url)
            return
        for house_link in house_links:
            house_id = house_link.rstrip('/').split('/')[-1].split('.')[0]
            # if self.collection.find({'house_id': house_id}).count() > 0:
            #     continue
            host = house_link.split(house_id)[0]
            url = host + f'canshu-{house_id}.html'
            # 基本参数
            yield Request(url,
                          callback=self.parse_house,
                          meta={
                              'house_id': house_id,
                              'city': self.city_dict[host]
                          })

            # 户型
            yield Request(url.replace('canshu', 'huxing'),
                          callback=self.parse_room_count)

            # 图片
            yield Request(url.replace('canshu', 'xiangce'),
                          callback=self.parse_pic,
                          meta={'house_id': house_id})

    def parse_house(self, response):
        house = {
            'sale_status': find(response, ajk_xp.SALE_STATUS),
            'telephone': '转'.join(find(response, ajk_xp.TELEPHONE, False)),
            'house_id': response.meta['house_id'],
            'city': response.meta['city'],
            'table': 'anjuke'
        }
        # 参数
        for item in response.xpath(ajk_xp.ITEMS):
            name = find(item, ajk_xp.NAME)
            if not name or name == '楼盘图片' or name == '售楼处电话':
                continue
            if name not in self.kw_dict:
                self.logger.warning('name %s unknown %s', name, response.url)
                continue
            if name in ['楼盘名称', '开发商', '物业公司']:
                value = find(item, './/a/text()') \
                        or find(item, './div[2]/text()')
            elif name in ['楼盘特点', '楼盘户型']:
                value = find(item, './/a/text()', False)
                if name == '楼盘户型':
                    value = house_type_split(value)
            # elif name == '售楼处电话':
            #     value = ' '.join(find(item, './/span/text()', False))
            elif name in ['区域位置', '参考单价']:
                value = ''.join(find(item, './/text()', False)).strip()
                value = value.lstrip(name).rstrip('[价格走势]').strip()
            else:
                value = find(item, './div[contains(@class, "des")]/text()')
            # self.logger.info('name %s, value %s', name, value)
            house[self.kw_dict[name]] = value

        yield house

    def parse_pic(self, response):
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
            'table': 'anjuke',
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

        # pic_des_list = self.ptn_pic_des.findall(html)
        # pic_url_list = self.ptn_pic_url.findall(html)
        # for label, pic_des, pic_url in zip(labels, pic_des_list, pic_url_list):
    # def parse_pic_url(self, response):
    #     urls = response.xpath(ajk_xp.PIC_HEAD_URLS)
    #     if not urls:
    #         self.logger.error('empty pictures %s', response.url)
    #         return
    #     for url in urls:
    #         yield Request(find(url, './@href'),
    #                       callback=self.parse_pic,
    #                       meta={'label': find(url, './text()')})
    #
    # def parse_pic(self, response):
    #     pics = response.xpath(ajk_xp.PIC)
    #     if not pics:
    #         self.logger.error('picture not found %s', response.url)
    #         return
    #     house_id = response.url.split('-')[-1].split('/')[0]
    #     yield {
    #         'house_id': house_id,
    #         'tag': 'album',
    #         'table': 'anjuke',
    #         'album': [
    #             {
    #                 'label': response.meta['label'],
    #                 'url': find(pic, './/img/@src'),
    #                 'title': find(pic, './a[@class="album-des"]/text()'),
    #                 'time': find(pic, './p[@class="album-time"]/text()')
    #             }
    #             for pic in pics
    #         ]
    #
    #     }
    def parse_pictorial(self, response):
        pic_items = response.xpath(ajk_xp.PIC_ITEMS)
        if not pic_items:
            self.logger.warning('pictorial is empty %s', response.url)
            return

        yield {
            'house_id': response.meta['house_id'],
            'tag': 'pictorial',
            'table': 'anjuke',
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
        total = find(response, ajk_xp.ROOM_COUNT)
        if not total:
            self.logger.warning('room count is empty. %s', response.url)
            return
        for page in range(1, int(ceil(int(total) / 8)) + 1):
            url = str(response.url).replace('.html', f'/s?p={page}')
            yield Request(url, callback=self.parse_room_url)

    def parse_room_url(self, response):
        urls = find(response, ajk_xp.ROOM_URLS, False)
        if not urls:
            self.logger.warning('room urls is empty. %s', response.url)
            return
        for url in urls:
            yield Request(url, callback=self.parse_room)

    def parse_room(self, response):
        room = {
            'house_id': response.url.split('/')[-1].split('-')[0],
            'table': 'anjuke_room'
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
        # titles = [i.strip()
        #           for i in find(response, ajk_xp.ROOM_TITLES).split(',')]
        # if len(titles) != 3:
        #     self.logger.error('room type titles error %s', response.url)
        # else:
        #     room['room_type'], room['house_type'] = titles[:-1]
        #     # re.findall('')
        #     if '约' in titles[-1]:
        #         room['area'] = titles[-1].split('约')[-1].strip('平米')
        #     else:
        #         room['area'] = titles[-1]
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
                if name not in self.room_price_dict:
                    self.logger.warning('key %s unknown %s', name, response.url)
                    continue
                room[self.room_price_dict[name]] = find(item, './span/text()')

        room_details = response.xpath(ajk_xp.ROOM_DETAILS)
        if not room_details:
            self.logger.warning('room details is empty %s', response.url)
        else:
            for item in room_details:
                name = find(item, './strong/text()')
                if name not in self.room_details_dict:
                    self.logger.warning('key %s unknown %s', name, response.url)
                    continue
                room[self.room_details_dict[name]] = find(item, './span/text()')

        room_description = find(response, ajk_xp.ROOM_DESCRIPTION, False)
        if not room_description:
            self.logger.warning('room description is empty %s', response.url)
        else:
            room['room_description'] = ' '.join(room_description)

        yield room


