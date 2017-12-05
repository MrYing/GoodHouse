"""
https://xa.fang.anjuke.com
created at 2017.12.4 by broholens
"""

"""
questions:

1. 如何选择城市
2. 取上整
3. 为什么不做成链接, 让用户直接访问安居客
4. 数据库设计
5. 1030/1185 redirect(/p2/)
"""

from math import ceil

from scrapy import Spider, Request
from pymongo import MongoClient

from GoodHouse.settings import MONGO_DATABASE, MONGO_URI
from GoodHouse.utils.f import find, house_type_split
from GoodHouse.xpath import anjuke_xpath as ajk_xp


class Anjuke(Spider):

    name = 'anjuke'

    start_urls = [
        'https://xa.fang.anjuke.com',  # xi'an
    ]

    city_dict = {
        'https://xa.fang.anjuke.com/loupan/': 'xian'
    }

    collection = MongoClient(MONGO_URI).client[MONGO_DATABASE].anjuke

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
        # '楼盘总价': 'total_price',
        # office
        '写字楼类型': 'office_building_type',
        '写字楼级别': 'office_building_level',
        '办公室面积': 'office_area',
        '招租客群': 'customer'
    }

    def parse(self, response):
        pages = response.xpath(ajk_xp.TOTAL_PAGES).extract_first()
        if not pages:
            self.logger.error('cannot find pages of %s', response.url)
            return
        pages = int(ceil(int(pages) / 50))
        # self.parse_house_link(response)

        for page in range(1, pages + 1):
            url = response.url.rstrip('/') + f'/loupan/all/p{page}/'
            yield Request(url, callback=self.parse_house_link)

    def parse_house_link(self, response):
        house_links = response.xpath(ajk_xp.HOUSE_LINKS).extract()
        if not house_links:
            self.logger.error('cannot find house_link of %s', response.url)
            return
        for house_link in house_links:
            house_id = house_link.rstrip('/').split('/')[-1].split('.')[0]
            # if self.collection.find({'house_id': house_id}).count() > 0:
            #     continue
            host = house_link.split(house_id)[0]
            url = host + f'canshu-{house_id}.html'
            # 参数
            yield Request(url,
                          callback=self.parse_house,
                          meta={
                              'house_id': house_id,
                              'city': self.city_dict[host]
                          })

            # # 图片
            # yield Request(url.replace('canshu', 'xiangce'),
            #               callback=)

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
            if not name or name == '楼盘图片':
                continue
            if name not in self.kw_dict:
                self.logger.warning('name %s unknown %s', name, response.url)
                continue
            if name in ['楼盘名称', '开发商', '物业公司']:
                value = find(item, './/a/text()')
            elif name in ['楼盘特点', '楼盘户型']:
                value = find(item, './/a/text()', False)
                if name == '楼盘户型':
                    value = house_type_split(value)
            # elif name == '售楼处电话':
            #     value = ' '.join(find(item, './/span/text()', False))
            elif name in ['区域位置', '参考单价']:
                value = ' '.join(find(item, './/text()', False)).strip()
                value = value.lstrip(name).rstrip('[价格走势]').strip()
            else:
                value = find(item, './div[contains(@class, "des")]/text()')
            # self.logger.info('name %s, value %s', name, value)
            house[self.kw_dict[name]] = value

        yield house

    def parse_room_count(self, response):
        total = find(response, ajk_xp.ROOM_COUNT)
        if not total:
            self.logger.error('room count is empty. %s', response.url)
            return
        for page in range(1, int(ceil(int(total / 8))) + 1):
            url = str(response.url).replace('.html', f'/s?p={page}')
            yield Request(url, callback=self.parse_room_url)

    def parse_room_url(self, response):
        urls = find(response, ajk_xp.ROOM_URLS, False)
        if not urls:
            self.logger.error('room urls is empty. %s', response.url)
            return
        for url in urls:
            yield Request(url, callback=self.parse_room)

    def parse_room(self, response):
        room = {
            'house_id': response.url.split('/')[-1].split('-')[0],
            'table': 'anjuke_room'
        }
        pics = find(response, ajk_xp.ROOM_TYPE_PICS, False)
        if not pics:
            self.logger.error('room pictures is empty. %s', response.url)
        else:
            room['pictures'] = [
                {
                    'pic_title': find(item, './/span[@class="title"]/text()'),
                    'pic_url': find(item, './/img/src')
                }
                for item in pics
            ]

        titles = [i.strip()
                  for i in find(response, ajk_xp.ROOM_TITLES).split(',')]
        if len(titles) != 3:
            self.logger.error('room type titles error %s', response.url)
        else:
            room['room_type'], room['house_type'] = titles[:-1]
            room['area'] = titles[-1].split('约').strip('平米')

        labels = find(response, ajk_xp.ROOM_LABELS, False)
        if not labels:
            self.logger.error('room labels is empty %s', response.url)
        else:
            room['sale_status'] = labels[0]
            room['labels'] = [label for label in labels[1:]]

        price = find(response, ajk_xp.ROOM_PRICE)
        if not price:
            self.logger.error('room price is empty %s', response.url)
        else:
            pass