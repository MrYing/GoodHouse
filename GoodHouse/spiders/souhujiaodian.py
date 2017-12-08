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

    kw_dict = {
        '楼盘名称': 'name',
        '建成年代': 'built_ear',
        '物业类型': 'property_type',
        '项目特色': 'labels',
        # '参考单价': 'price',
        '建筑类型': 'building_type',
        '装修标准': 'decoration_standards',
        '产权年限': 'durable_years',
        '装修情况': 'renovation_condition',
        '开发商': 'developer',
        '环线位置': 'loop_location',
        '投资商': 'investor',
        '品牌商': 'brand',
        '楼盘地址': 'address',
        # '区域位置': 'region',
        '销售状态': 'sale_status',
        '开盘时间': 'opening_time',
        '交房时间': 'delivery_time',
        '售楼电话': 'telephone',
        '轨道交通': 'rail',
        '公交路线': 'bus',
        '交通方式': 'transportation',
        '占地面积': 'land_area',
        '建筑面积': 'total_area',
        '容积率': 'floor_area_ratio',
        '绿化率': 'green_ratio',
        '车位数': 'parking_count',
        '楼栋总数': 'building_count',
        '总户数': 'householder_count',
        '物业费': 'property_fee',
        '周边配套': 'peripheral_facilities',
        '学校': 'school',
        '内部配套': 'internal_facilities',
        '建材设备': 'building_material_equipment',
        '供暖方式': 'heating_method',
        # '最低首付': 'min_deposit',
        # '楼盘优惠': 'discount',
        # '楼盘户型': 'house_type',
        # # '售楼处地址': 'sale_address',
        # '预售许可证': 'license',
        #
        # '规划户数': 'householder_count',
        # '楼层状况': 'story_status',
        # '工程进度': 'project_progress',
        #
        # '物业公司': 'property_company',
        #
        # '车位比': 'parking_ratio',
        # # business
        # '开间面积': 'room_area',
        # '商业面积': 'business_area',
        # '总建筑面积': 'total_area',
        # '招商业态': 'business_model',
        # '临近商圈': 'near_business',
        # '周边人群': 'surrounding_people',
        # '出售类型': 'sale_type',
        # '得房率': 'room_rate',
        # '商铺总套数': 'shops_count',
        # '是否统一管理': 'is_unified_management',
        # '是否分割': 'is_segmentation',
        # '出租类型': 'rent_type',
        # '租金': 'rent',
        # '是否包含物业费': 'contain_property_fee',
        # '待租面积': 'for_rent_area',
        # '待租套数': 'for_rent_count',
        # '月供': 'monthly_payment',
        # '楼盘总价': 'total_price',
        # '标准层面积': 'standard_area',
        # '公共部分精装修': 'public_exquisite',
        # '临近CBD': 'cbd',
        # '已签约租户': 'tenants',
        # '已签约商户': 'tenants',
        # # office
        # '写字楼类型': 'office_building_type',
        # '写字楼级别': 'office_building_level',
        # '办公室面积': 'office_area',
        # '招租客群': 'customer'
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
                          callback=self.parse_xiangqing,
                          meta={
                              'host': response.meta['host'],
                              'house_id': house_id
                          })
            # 户型
            yield Request(url=response.meta['host']+house_id+'/huxing/',
                          callback=self.parse_huxing)
            # 相册
            yield Request(url=response.meta['host']+house_id+'/xiangce/',
                          callback=self.parse_xiangce)

    def parse_xiangqing(self, response):
        house = {
            'city': self.city_dict[response.meta['host']],
            'table': 'souhujiaodian',
            'house_id': response.meta['house_id'],
            'alias_name': find(response, shjd_xp.OTHER_NAME),
        }

        base_items = response.xpath(shjd_xp.INFO)
        if not base_items:
            self.logger.error('base info is empty! %s', response.url)
            return
        for item in base_items:
            self.base(house, item, 'l')
            self.base(house, item, 'r')

        licenses = response.xpath(shjd_xp.LICENSE)
        if not licenses:
            self.logger.error('base info is empty! %s', response.url)
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
            self.logger.error('price unreachable! %s', response.url)
        else:
            house['price'] = [
                {
                    'release_time': find(item, './td[1]/span/text()'),
                    'highest_price': find(item, './td[2]/text()'),
                    'avg_price': find(item, './td[3]/span/text()'),
                    'lowest_price': find(item, './td[4]/text()'),
                    'price_details': find(item, './td[5]/text()')
                }
                for item in price
            ]

        house['description'] = find(response, shjd_xp.DESCRIPTION)

    def base(self, house, item, d):
        key = find(item, f'./td[@class="label-{d}"]/text()') and \
            find(item, f'./td[@class="label-{d}"]/text()').strip('：')
        value = find(item, f'./td[@class="text-{d}"]/text()') or \
            find(item, f'./td[@class="text-full"]/text()')
        if not key or key == '售楼地址':
            return

        if not self.kw_dict.get(key):
            self.logger.warning('unknown key %s', key)
            return
        house[self.kw_dict[key]] = value

    def license(self, response):
        pass

    def parse_huxing(self, response):
        pass

    def parse_xiangce(self, response):
        pass