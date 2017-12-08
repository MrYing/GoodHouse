
import logging
from random import choice
from operator import itemgetter

import requests

from GoodHouse.settings import AMAP_KEYS


class LBS:

    logger = logging.Logger(__name__)
    logger.setLevel('INFO')

    to_ip_url = 'http://restapi.amap.com/v3/geocode/geo?key={}&address={}&city={}'
    to_poi_url = 'http://restapi.amap.com/v3/place/around?key={}&location={}&radius={}&types={}'

    pois = [
        {'code': '060400', 'name': 'supermarket', 'radius': 1000},
        {'code': '060200', 'name': 'retail_store', 'radius': 500},
        {'code': '060100', 'name': 'shopping_center', 'radius': 1500},
        {'code': '050000', 'name': 'catering_service', 'radius': 1000},
        {'code': '080600', 'name': 'theater', 'radius': 1000},
        {'code': '100100', 'name': 'hotel', 'radius': 1000},
        {'code': '141203', 'name': 'primary_school', 'radius': 1000},
        {'code': '141202', 'name': 'middle_school', 'radius': 2000},
        {'code': '141201', 'name': 'high_school', 'radius': 500},
        {'code': '140100|140200|140300|140400|140500|140600|140700|140800|140900', 'name': 'museum', 'radius': 1000},
        {'code': '150700', 'name': 'bus', 'radius': 1000},
        {'code': '150500', 'name': 'subway', 'radius': 1200},
        {'code': '150201', 'name': 'train', 'radius': 10000},
        {'code': '150100', 'name': 'plane', 'radius': 25000},
        {'code': '150400', 'name': 'coach', 'radius': 10000},
        {'code': '190304|190305|190308|190309', 'name': 'exit_entrance', 'radius': 10000},
        {'code': '090000', 'name': 'medical_service', 'radius': 2000},
        {'code': '160100', 'name': 'bank', 'radius': 1500},
        {'code': '160300', 'name': 'ATM', 'radius': 1200},
        {'code': '141101|141102', 'name': 'radiation_pollution', 'radius': 500},
        # {'code': '141101|141102', 'name': '辐射污染', 'radius': 500, 'f': self.fswr},
        {'code': '010100|010200|010300', 'name': 'gas', 'radius': 500},
        {'code': '071900', 'name': 'funeral_parlor', 'radius': 5000},
        {'code': '110101|110102|110103|110104', 'name': 'park', 'radius': 2000},
        {'code': '110105|110106', 'name': 'square', 'radius': 2000},
        {'code': '190204|190205', 'name': 'water_system', 'radius': 2000},
        {'code': '110200', 'name': 'scenic_area', 'radius': 2000},
        # {'code': '110100|110200|190204|190205', 'name': '自然环境', 'radius': 2000}
    ]

    # '060400'  # 超市
    # '060200'  # 便利店
    # '060100'  # 购物中心
    # '050000'  # 餐饮
    # '080600'  # 影剧院
    # '100100'  # 酒店宾馆
    # '141201'  # 大学
    # '141202'  # 中学
    # '141203'  # 小学
    # '140100|140200|140300|140400|140500|140600|140700|140800|140900'  # 博物馆
    # '150700'  # 公交
    # '150500'  # 地铁
    # '150201'  # 火车站
    # '150100'  # 机场
    # '150400'  # 长途汽车站
    # '190304|190305|190308|190309'  # 城市快速干道、高速出入口
    # '090000'  # 医疗
    # '160100'  # 营业厅
    # '160300'  # ATM
    # '141101|1411020|10100|010200|010300'  # 电视台 电台（辐射） 加油站
    # '071900'  # 殡仪馆
    # '110100|190204|190205|110200'  # 公园广场 河流 湖泊 景点
    def get_ip(self, item):
        address = item.get('region', '') + item['address'] + item['name']
        url = self.to_ip_url.format(choice(AMAP_KEYS),
                                    address,
                                    item['city'])
        result = requests.get(url).json()
        if int(result.get('count', 0)) == 0:
            self.logger.error('can not find ip %s', url)
            return item

        self.logger.info('get ip! %s', url)
        result = result['geocodes'][0]

        item.update({
            'formatted_address': result['formatted_address'],
            'province': result['province'],
            'district': result['district'],
            'location': result['location']
        })
        return item

    def get_poi(self, item):
        item = self.get_ip(item)

        result = {}
        for poi in self.pois:
            url = self.to_poi_url.format(
                choice(AMAP_KEYS), item['location'], poi['radius'], poi['code']
            )
            poi_results = requests.get(url).json()

            if int(poi_results.get('infocode', 0)) != 10000:
                self.logger.error('can not find pois %s', url)
                result[poi['name']] = []
                continue

            result[poi['name']] = self.sort_pois(poi_results.get('pois'))

        self.logger.info('get pois! %s', item['name'])
        return item.update({'pois': result})

    def sort_pois(self, pois_raw):
        # TODO: 只拿前20个
        return pois_raw and sorted([
            {
                'poi_name': poi['name'],
                'poi_address': poi['address'],
                'poi_location': poi['location'],
                'poi_distance': int(poi['distance'])
            }
            for poi in pois_raw
        ], key=itemgetter('poi_distance'))

    # def ATM(self, sorted_pois):
    #     pass
    #
    # def zrhj(self, nearest):
    #     """
    #     包括： 公园 广场 水系 景点
    #     :param pois:
    #     :return:
    #     """
    #     if nearest < 100: return 100
    #     elif nearest < 300: return 85
    #     elif nearest < 500: return 75
    #     elif nearest < 800: return 55
    #     elif nearest < 1200: return 40
    #     elif nearest < 1600: return 25
    #     elif nearest < 2000: return 10
    #     else: return 0
    #
    # def cs(self, count):
    #     """
    #     超市 同 购物中心 酒店宾馆 博物馆
    #     3家以上100分；2家，80分；1家，60分；没有0分
    #     :param count:
    #     :return:
    #     """
    #     return {2: 80, 1: 60, 0: 0}.get(count, 100)
    #
    # def bld(self, count):
    #     """
    #     便利店 同 餐饮服务
    #     ≥5家100分；≥3家80分；≥1家50分；没有0分
    #     :param count:
    #     :return:
    #     """
    #     # if count >= 5:
    #     #     return 100
    #     # elif count >= 3:
    #     #     return 80
    #     # elif count >= 1:
    #     #     return 50
    #     # return 0
    #     return {0: 0, 1: 50, 2: 50, 3: 80, 4: 80}.get(count, 100)
    #
    # def yjy(self, count):
    #     """
    #     影剧院
    #     2家以上100分；1家60分；没有0分
    #     :param count:
    #     :return:
    #     """
    #     return {0: 0, 1: 60}.get(count, 100)
    #
    # def gj_1(self, count):
    #     """
    #     1公里以内公交线路
    #     :param count:
    #     :return:
    #     """
    #     return {0: 0, 1: 20, 2: 40, 3: 40,
    #             4: 60, 5: 60, 6: 75, 7: 75, 8: 90, 9: 90}.get(count, 100)
    #
    # def yh_1(self, count):
    #     """
    #     银行营业厅 同 ATM
    #     5家，100分，3-5家，80分；2-3家，60分；1家，40分；0家不得分
    #     :param count:
    #     :return:
    #     """
    #     return {0: 0, 1: 40, 2: 60, 3: 80, 4: 80}.get(count, 100)
    #
    # def fswr(self, count):
    #     """
    #     辐射污染 同殡仪馆
    #     :param count:
    #     :return:
    #     """
    #     return 0 if count == 0 else 100



