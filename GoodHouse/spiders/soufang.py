"""
https://xa.fang.anjuke.com
created at 2017.12.13 by broholens
"""

import re

from scrapy import Spider, Request

from GoodHouse.utils.f import find
from GoodHouse.xpath import soufang as sf
from GoodHouse.settings import CITY


class Soufang(Spider):

    name = 'soufang'

    start_urls = [
        'http://newhouse.xian.fang.com/house/s/'
    ]

    picture_url = '{}/house/ajaxrequest/photolist_get.php?newcode={}&type={}&nextpage={}'
    huxing_url = '{}/house/ajaxrequest/householdlist_get.php?newcode={}&count=false&start=0&limit=100&room=all'

    kw_dict = {
        '物业类别：': 'property_type',
        '建筑类别：': ('building_type', './div[2]/span/text()'),
        '装修状况：': 'renovation_condition',
        '产权年限：': ('durable_years', './div[2]/div/p/text()'),
        '环线位置：': 'region',
        '开': ('developer', './div[2]/a/text()'),
        '楼盘地址：': 'address',
        '销售状态：': 'sale_status',
        '楼盘优惠：': 'discount',
        '开盘时间：': 'opening_time',
        '交房时间：': 'delivery_time',
        '售楼地址：': 'sale_address',
        '咨询电话：': 'telephone',
        '主力户型：': ('house_type', './div[2]/a/text()'),

        '交通': ('transportation', './text()'),
        '中小学': ('school', './text()'),
        '综合商场': ('general_store', './text()'),
        '医院': ('hospital', './text()'),
        '其他': ('peripheral_facilities', './text()'),

        '占地面积：': 'land_area',
        '建筑面积：': 'total_area',
        '容': 'floor_area_ratio',
        '绿': 'green_ratio',
        '停': 'parking_count',
        '楼栋总数：': 'building_count',
        '总': 'householder_count',
        '物业公司：': ('property_company', './div[2]/a/text()'),
        '物': 'property_fee',
        '物业费描述：': 'property_fee_description',
        '楼层状况：': 'story_status',
    }

    ptn_house_id = re.compile('showhouseid\':\'(.*?)\'')

    def parse(self, response):
        pages = find(response, sf.PAGE_COUNT)
        if not pages:
            self.logger.error('cannot find pages of %s', response.url)
            return

        pages = int(pages.strip('/'))
        for page in range(1, pages + 1):
            url = response.url.rstrip('/') + f'/b9{page}/'
            yield Request(url, callback=self.parse_house_link)

    def parse_house_link(self, response):
        house_links = find(response, sf.HOUSE_LINK, False)
        if not house_links:
            self.logger.error('cannot find house_link of %s', response.url)
            return
        house_ids = self.ptn_house_id.findall(response.text)
        if not house_ids:
            self.logger.error('house ids not found! %s', response.url)
            return
        # house_labels = response.content.decode('gb2312', 'replace')
        city = response.url.split('.fang.')[0].split('.')[-1]
        house_ids = house_ids[0].split(',')
        for house_link, house_id in zip(house_links, house_ids):
            house_link = house_link.split('/?')[0]
            # 基本参数
            yield Request(house_link + f'house/{house_id}/housedetail.htm',
                          callback=self.parse_house,
                          meta={
                              'house_id': house_id,
                              'city': city
                          })

            # 户型
            yield Request(self.huxing_url.format(house_link, house_id),
                          callback=self.parse_room,
                          meta={'house_id': house_id})

            # 图片
            yield Request(house_link + f'photo/{house_id}.htm',
                          callback=self.parse_pic_link,
                          meta={'house_id': house_id})

    def parse_house(self, response):
        house = {
            'house_id': response.meta['house_id'],
            'city': CITY[response.meta['city']],
            'table': self.name,
            'name': find(response, sf.NAME),
            'alias': find(response, sf.ALIAS),
            'labels': find(response, sf.LABELS, False),
            'price': find(response, sf.PRICE),
            'description': find(response, sf.DESCRIPTION)
        }
        # 参数
        for item in response.xpath(sf.INFO):
            name = find(item, './div[1]/text() | ./span/text()')
            if not name or name == '项目特色：':
                continue
            if name not in self.kw_dict:
                self.logger.warning('name %s unknown %s', name, response.url)
                continue
            name = self.kw_dict[name]
            if isinstance(name, str):
                value = find(item, './div[2]/text()')
            else:
                name, value = name[0], find(item, name[1])
            house[name] = value

        licenses = response.xpath(sf.LICENSE)
        if not licenses:
            self.logger.warning('license unreachable! %s', response.url)
        else:
            house['license'] = [
                {
                    'license_number': find(item, './td[1]/text()'),
                    'license_start_at': find(item, './td[2]/text()'),
                    'bind_building': find(item, './td[3]/text()'),
                }
                for item in licenses
            ]

        price = response.xpath(sf.PRICE)
        if not price:
            self.logger.warning('price unreachable! %s', response.url)
        else:
            house['price_history'] = [
                {
                    'release_time': find(item, './td[1]/text()'),
                    'avg_price': find(item, './td[2]/text()'),
                    'lowest_price': find(item, './td[3]/text()'),
                    'price_details': find(item, './td[4]/text()')
                }
                for item in price
            ]
        self.logger.warning('house: %s', house)

        # yield house

    def parse_pic_link(self, response):
        pics = response.xpath(sf.PICS)
        if not pics:
            self.logger.warning('pictures -a unreachable %s', response.url)
            return
        host = response.url.split('/photo')[0]
        for pic in pics:
            pic_total_num = find(pic, './em/text()')
            pic_label = find(pic, './span/text()')
            if pic_label == '户型':
                continue
            pic_id = find(pic, './@href').split('list_')[-1].split('_')[0]
            # TODO: 只拿了前6个,后面的要拿的话 parse_pic yield后会在 mongopipeline
            # TODO: set item, 会将前面的覆盖
            # for page in range(1, int(pic_total_num / 6) + 1):
            #     url = self.picture_url.format(host,
            #                                   response.meta['house_id'],
            #                                   pic_id,
            #                                   page)
            #     yield Request(url=url,
            #                   callback=self.parse_pic,
            #                   meta={'label': pic_label})
            url = self.picture_url.format(host,
                                          response.meta['house_id'],
                                          pic_id,
                                          1)
            yield Request(url=url,
                          callback=self.parse_pic,
                          meta={
                              'label': pic_label,
                              'house_id': response.meta['house_id'],
                          })

    def parse_pic(self, response):
        # yield {
        #     'house_id': response.meta['house_id'],
        #     'tag': 'album',
        #     'table': self.name,
        #     'album': [
        #         {
        #             'picture_label': response.meta['label'],
        #             'picture_url': pic['url'],
        #             'picture_description': pic['tital']
        #         }
        #         for pic in response.json()
        #     ]
        # }
        self.logger.warning('picture %s', {
            'house_id': response.meta['house_id'],
            'tag': 'album',
            'table': self.name,
            'album': [
                {
                    'picture_label': response.meta['label'],
                    'picture_url': pic['url'],
                    'picture_description': pic['tital']
                }
                for pic in response.json()
            ]
        })

    def parse_room(self, response):
        for room in response.json():
            # yield {
            #     'table': self.name + '_room',
            #     'house_id': response.meta['house_id'],
            #     'reference_price': room['reference_price'] +
            #                        room['reference_price_type'],
            #     'room_score': room['hx_score'],
            #     'room_description': room['hx_desp'],
            #     'room_labels': room['huxing_feature'].split(','),
            #     'room_type': room['housetitle'],
            #     'house_type': '{}室{}厅{}卫{}厨'.format(room['room'],
            #                                            room['hall'],
            #                                            room['toilet'],
            #                                            room['kitchen']),
            #     'house_area': room['buildingarea'] + '平方米',
            #     'room_sale_status': room['status'],
            #     'room_album': [{
            #         'picture_url': room['houseimageurl'],
            #         'picture_title': room['housetitle']
            #     }]
            # }
            self.logger.warning('room %s', {
                'table': self.name + '_room',
                'house_id': response.meta['house_id'],
                'reference_price': room['reference_price'] +
                                   room['reference_price_type'],
                'room_score': room['hx_score'],
                'room_description': room['hx_desp'],
                'room_labels': room['huxing_feature'].split(','),
                'room_type': room['housetitle'],
                'house_type': '{}室{}厅{}卫{}厨'.format(room['room'],
                                                    room['hall'],
                                                    room['toilet'],
                                                    room['kitchen']),
                'house_area': room['buildingarea'] + '平方米',
                'room_sale_status': room['status'],
                'room_album': [{
                    'picture_url': room['houseimageurl'],
                    'picture_title': room['housetitle']
                }]
            })