"""
https://xian.focus.cn/loupan/171918/xiangqing.html
created at 2017.12.4 by broholens
"""

from math import ceil

from scrapy import Spider, Request

from GoodHouse.utils.f import find
from GoodHouse.xpath import souhujiaodian as shjd_xp
from GoodHouse.settings import CITY


class Souhujiaodian(Spider):

    name = 'souhujiaodian'

    start_urls = [
        'https://xian.focus.cn/loupan/',
        'https://house.focus.cn/loupan/',
        'https://sh.focus.cn/loupan/',
        'https://gz.focus.cn/loupan/',
        # 'http://sz.focus.cn/search/index.html',
        'https://hz.focus.cn/loupan/'

    ]

    kw_dict = {
        '楼盘名称': 'name',
        '建成年代': 'built_ear',
        '物业类型': 'property_type',
        '项目特色': 'features',
        # '参考单价': 'price',
        '建筑类型': 'building_type',
        '装修标准': 'decoration_standards',
        '产权年限': 'durable_years',
        '装修情况': 'renovation_condition',
        '开发商': 'developer',
        '环线位置': 'region',  # 'loop_location',
        '投资商': 'investor',
        '品牌商': 'brand',
        '楼盘地址': 'address',
        # '区域位置': 'region',
        '销售状态': 'sale_status',
        '开盘时间': 'opening_time',
        '交房时间': 'delivery_time',
        '售楼地址': 'sale_address',
        '售楼电话': 'telephone',
        '轨道交通': 'rail',
        '公交路线': 'bus',
        '交通方式': 'transportation',
        '占地面积': 'land_area',
        '建筑面积': 'total_area',
        '容积率': 'floor_area_ratio',
        '绿化率': 'green_ratio',
        '车位数': 'parking_count',
        '停车位': 'parking_count',
        '楼栋总数': 'building_count',
        '总户数': 'householder_count',
        '物业费': 'property_fee',
        '周边配套': 'peripheral_facilities',
        '学校': 'school',
        '内部配套': 'internal_facilities',
        '建材设备': 'building_material_equipment',
        '供暖方式': 'heating_method',
        '物业公司': 'property_company',
    }

    room_details_dict = {
        '居     室：': 'house_type',
        '层   高：': 'house_storey_height',
        '户型朝向：': 'house_distribution',
        '总套数：': 'house_count',
        '建筑面积：': 'house_area'
    }

    def parse(self, response):
        total_count = find(response, shjd_xp.TOTAL_COUNT)
        if not total_count:
            self.logger.error('total count not clear! %s', response.url)
            return
        total_pages = int(ceil(int(total_count) / 20))
        if response.url.startswith('http://sz.focus.cn/'):
            url = response.url.strip('.html') + '_p{}' + '.html'
            url_xiangqing = 'http://sz.focus.cn/loupan/' + '{}/xiangxi/'
            url_huxing = 'http://sz.focus.cn/loupan/' + '{}/huxing/'
            url_xiangce = 'http://sz.focus.cn/loupan/' + '{}/tu/'
        else:
            url = response.url + 'p{}/'
            url_xiangqing = response.url + '{}/xiangqing.html'
            url_huxing = response.url + '{}/huxing/'
            url_xiangce = response.url + '{}/xiangce/'
        for page in range(1, total_pages + 1):
            yield Request(url.format(page),
                          callback=self.parse_house_link,
                          meta={
                              'xq': url_xiangqing,
                              'hx': url_huxing,
                              'xc': url_xiangce
                          })

    def parse_house_link(self, response):
        house_ids = find(response, shjd_xp.HOUSE_IDS, False)
        if not house_ids:
            self.logger.error('house ids not clear! %s', response.url)
            return

        for house_id in house_ids:
            # 详情
            yield Request(url=response.meta['xq'].format(house_id),
                          callback=self.parse_xiangqing,
                          meta={'house_id': house_id})
            # 户型
            yield Request(url=response.meta['hx'].format(house_id),
                          callback=self.parse_huxing_link,
                          meta={'house_id': house_id})
            # 相册
            yield Request(url=response.meta['xc'].format(house_id),
                          callback=self.parse_xiangce_link,
                          meta={'house_id': house_id})

    def parse_xiangqing(self, response):
        city = response.url.split('.')[0].split('/')[-1]
        house = {
            'city': CITY[city],
            'table': 'souhujiaodian',
            'house_id': response.meta['house_id'],
            'alias_name': find(response, shjd_xp.OTHER_NAME),
        }
        labels = find(response, shjd_xp.LABELS, False)
        if not labels:
            self.logger.warning('empty labels! %s', response.url)
        else:
            house['labels'] = labels

        base_items = response.xpath(shjd_xp.INFO)
        if not base_items:
            self.logger.warning('base info is empty! %s', response.url)
        else:
            for item in base_items:
                self.base(house, item, 'l')
                self.base(house, item, 'r')

        licenses = response.xpath(shjd_xp.LICENSE)
        if not licenses:
            self.logger.warning('license info is empty! %s', response.url)
        else:
            house['license'] = [
                {
                    'license_number': find(item, './td[1]/text()'),
                    'license_start_at': find(item, './td[2]/span/text()'),
                    'bind_building': find(item, './td[3]/text()'),
                }
                for item in licenses
            ]

        price = response.xpath(shjd_xp.PRICE)
        if not price:
            self.logger.warning('price unreachable! %s', response.url)
        else:
            house['price_history'] = [
                {
                    'release_time': find(item, './td[1]/span/text()'),
                    # 'highest_price': find(item, './td[2]/text()'),
                    # 'avg_price': find(item, './td[3]/span/text()'),
                    # 'lowest_price': find(item, './td[4]/text()'),
                    'price_details': find(item, './td[last()]/text()')
                }
                for item in price
            ]
            house['price'] = house['price_history'][0]['price_details']

        house['description'] = find(response, shjd_xp.DESCRIPTION)

        yield house

    def base(self, house, item, d):
        key = find(item, f'./td[@class="label-{d}"]/text()') and \
            find(item, f'./td[@class="label-{d}"]/text()').strip('：')
        value = find(item, f'./td[@class="text-{d}"]/text()') or \
            find(item, f'./td[@class="text-full"]/text()')
        if not key:
            return

        if not self.kw_dict.get(key):
            self.logger.warning('unknown key %s', key)
            return
        house[self.kw_dict[key]] = value

    def parse_xiangce_link(self, response):
        pics = response.xpath(shjd_xp.PICTURE_URLS)
        if not pics:
            self.logger.warning('picture unreachable! %s', response.url)
            return
        for pic in pics:
            yield Request(url=find(pic, './@href'),
                          callback=self.parse_xiangce,
                          meta={
                              'house_id': response.meta['house_id'],
                              'label': find(pic, './text()').split('(')[0]
                          })

    def parse_xiangce(self, response):
        yield {
            'house_id': response.meta['house_id'],
            'tag': 'album',
            'table': 'souhujiaodian',
            'album': [
                {
                    'picture_url': find(img, './@src'),
                    'picture_label': response.meta['label'],
                    'picture_description': find(img, './@data-name')
                }
                for img in response.xpath(shjd_xp.PICTURES)
            ]
        }

    def parse_huxing_link(self, response):
        rooms = find(response, shjd_xp.ROOM, False)
        if not rooms:
            self.logger.warning('room urls unreachable! %s', response.url)
            return
        for room in rooms:
            yield Request(room,
                          callback=self.parse_huxing,
                          meta={'house_id': response.meta['house_id']})

    def parse_huxing(self, response):
        room = {
            'house_id': response.meta['house_id'],
            'table': 'souhujiaodian_room',
        }

        room_pics = find(response, shjd_xp.ROOM_PICS, False)
        if not room_pics:
            self.logger.warning('room pictures unreachable! %s', response.url)
        else:
            room['room_album'] = [{'picture_url': img} for img in room_pics]

        room['room_type'] = find(response, shjd_xp.ROOM_TYPE)
        room['room_sale_status'] = find(response, shjd_xp.SALE_STATUS)
        price = ''.join(find(response, shjd_xp.ROOM_PRICE, False))
        room['reference_price'] = price

        room_info = response.xpath(shjd_xp.ROOM_INFO)
        if not room_info:
            self.logger.warning('room info unreachable! %s', response.url)
        else:
            for item in room_info:
                key = find(item, './label/text()')
                self.room_details_dict[key] = find(item, './text()')

        room_des = response.xpath(shjd_xp.ROOM_DESCRIPTION)
        if not room_des:
            self.logger.warning('room description empty! %s', response.url)
        else:
            room['room_description'] = find(room_des, '../div/text()')

        yield room

