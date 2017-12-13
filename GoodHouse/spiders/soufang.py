"""
https://xa.fang.anjuke.com
created at 2017.12.13 by broholens
"""

import re
import json

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
        '产权年限：': ('durable_years', './div[2]/div/p/text() | ./div[2]/text()'),
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
        '其他': ('entertainment', './text()'),
        '邮政': ('post_office', './text()'),
        '银行': ('bank', './text()'),
        '幼儿园': ('kindergarten', './text()'),
        '大学': ('university', './text()'),
        '小区内部配套': ('peripheral_facilities', './text()'),

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

        '写字楼级别：': 'office_building_level',
        '楼栋情况：': 'story_status',
        '所属商圈：': 'near_business',
        '标准层面积：': 'standard_area',
        '单套面积：': 'single_area',
        '商业面积：': 'business_area',
        '办公面积：': 'office_area',
        '开间面积：': 'room_area',
        '标准层高：': 'standard_floor_height',
        '装修情况：': 'renovation_condition',
        '楼层说明：': 'floor_description',
        '物业费：': 'property_fee',
        '物业说明：': 'property_fee_description',
        '供暖方式：': 'heating_method',
        '水电类别：': 'hydropower_category',
        '停车位配置：': 'parking_count',
        '电梯配置：': 'elevator',
        '嫌恶设施': 'nasty_facility'
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
            if not name or name in ['项目特色：', '楼盘特色：', '预售许可证：']:
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

        history = response.xpath(sf.HISTORY)
        if not history:
            self.logger.warning('history unreachable! %s', response.url)
        else:
            if len(history) > 1:
                licenses = history[0].xpath('.//tr[position()>1]')
                house['license'] = [
                    {
                        'license_number': find(item, './td[1]/text()'),
                        'license_start_at': find(item, './td[2]/text()'),
                        'bind_building': find(item, './td[3]/text()'),
                    }
                    for item in licenses
                ]
                price = history[1].xpath('.//tr[position()>1]')
            else:
                price = history[0].xpath('.//tr[position()>1]')

            house['price_history'] = [
                {
                    'release_time': find(item, './td[1]/text()'),
                    'price_details': find(item, './td[last()]/text()')
                }
                for item in price
            ]

        yield house

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
            for page in range(1, int(int(pic_total_num) / 6) + 1):
                url = self.picture_url.format(host,
                                              response.meta['house_id'],
                                              pic_id,
                                              page)
                yield Request(url=url,
                              callback=self.parse_pic,
                              meta={
                                  'label': pic_label,
                                  'house_id': response.meta['house_id'],
                              })

    def parse_pic(self, response):
        if response.meta['label'] == '装修案例':
            album = [
                {
                    'picture_label': response.meta['label'],
                    'picture_url': pic.get('picurl', ''),
                    'picture_description': pic.get('case_name', '')
                }
                for pic in json.loads(response.text).get('caselist', [])
            ]
        elif response.meta['label'] == '360全景看房':
            album = [
                {
                    'picture_label': response.meta['label'],
                    'picture_url': pic.get('house_url', '')
                }
                for pic in json.loads(response.text)
            ]
        elif response.meta['label'] == '楼盘视频':
            album = [
                {
                    'picture_label': response.meta['label'],
                    'picture_url': pic.get('Vsurl', ''),
                    'upload_date': pic.get('registdate', '')
                }
                for pic in json.loads(response.text).get('list', [])
            ]
        else:
            album = [
                {
                    'picture_label': response.meta['label'],
                    'picture_url': pic.get('url', ''),
                    'picture_description': pic.get('title', '')
                }
                for pic in json.loads(response.text)
            ]

        yield {
            'house_id': response.meta['house_id'],
            'tag': 'album',
            'table': self.name,
            'album': album
        }

    def parse_room(self, response):
        for room in json.loads(response.text):
            yield {
                'table': self.name + '_room',
                'house_id': response.meta['house_id'],
                'reference_price': room['reference_price'] +
                                   room['reference_price_type'],
                'room_score': room.get('hx_score', ''),
                'room_description': room.get('hx_desp', ''),
                'room_labels': room.get('huxing_feature').split(','),
                'room_type': room.get('housetitle'),
                'house_type': '{}室{}厅{}卫{}厨'.format(room['room'],
                                                       room['hall'],
                                                       room['toilet'],
                                                       room['kitchen']),
                'house_area': room.get('buildingarea', '') + '平方米',
                'room_sale_status': room.get('status', ''),
                'room_album': [{
                    'picture_url': room.get('houseimageurl', ''),
                    'picture_title': room.get('housetitle', '')
                }]
            }
