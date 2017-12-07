
import logging
from random import choice

import requests

from GoodHouse.settings import AMAP_KEYS

logger = logging.Logger(__name__)

to_ip_url = 'http://restapi.amap.com/v3/geocode/geo?key={}&address={}&city={}'
to_poi_url = 'http://restapi.amap.com/v3/place/around?key={}&location={}&radius={}&types={}'

arounds = [
    {'code': '060400', 'name': '超市', 'radius': 1000},
    {'code': '060200', 'name': '便利店', 'radius': 500},
    {'code': '060100', 'name': '购物中心', 'radius': 1500},
    {'code': '050000', 'name': '餐饮服务', 'radius': 1000},
    {'code': '080600', 'name': '影剧院', 'radius': 1000},
    {'code': '100100', 'name': '酒店宾馆', 'radius': 1000},
    {'code': '141203', 'name': '小学', 'radius': 1000},
    {'code': '141202', 'name': '中学', 'radius': 2000},
    {'code': '141201', 'name': '大学', 'radius': 500},
    {'code': '140100|140200|140300|140400|140500|140600|140700|140800|140900', 'name': '博物馆', 'radius': 1000},
    {'code': '150700', 'name': '公交', 'radius': 1000},
    {'code': '150500', 'name': '地铁', 'radius': 1200},
    {'code': '150201', 'name': '火车', 'radius': 10000},
    {'code': '150100', 'name': '飞机', 'radius': 25000},
    {'code': '150400', 'name': '长途汽车', 'radius': 10000},
    {'code': '190304|190305|190308|190309', 'name': '城市快速干道高速出入口', 'radius': 10000},
    {'code': '090000', 'name': '医疗', 'radius': 2000},
    {'code': '160100', 'name': '银行营业厅', 'radius': 1500},
    {'code': '160300', 'name': 'ATM', 'radius': 1200},
    {'code': '141101|1411020|10100|010200|010300', 'name': '辐射污染', 'radius': 500},
    {'code': '071900', 'name': '殡仪馆', 'radius': 5000},
    {'code': '110100|190204|190205|110200', 'name': '自然环境', 'radius': 2000}
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


def get_ip(item):
    address = item['region'] + item['address'] + item['name']
    url = to_ip_url.format(choice(AMAP_KEYS),
                           address,
                           item['city'])
    result = requests.get(url).json()
    if int(result.get('count', 0)) == 0:
        logger.error('can not find ip %s', url)
        return item
    result = result['geocodes'][0]

    item.update({
        'formatted_address': result['formatted_address'],
        'province': result['province'],
        'district': result['district'],
        'location': result['location']
    })
    return item


def get_poi(location):
    result = {}
    for around in arounds:
        url = to_poi_url.format(
            choice(AMAP_KEYS), location, around['radius'], around['code']
        )
        poi = requests.get(url).json()

        if int(poi.get('infocode', 0)) != 10000:
            logger.error('can not find poi %s', url)
            continue
        result[]


def cs(count):
    """
    超市 同 购物中心 酒店宾馆 博物馆
    3家以上100分；2家，80分；1家，60分；没有0分
    :param count:
    :return:
    """
    return {2: 80, 1: 60, 0: 0}.get(count, 100)

def bld(count):
    """
    便利店 同 餐饮服务
    ≥5家100分；≥3家80分；≥1家50分；没有0分
    :param count:
    :return:
    """
    # if count >= 5:
    #     return 100
    # elif count >= 3:
    #     return 80
    # elif count >= 1:
    #     return 50
    # return 0
    return {0: 0, 1: 50, 2: 50, 3: 80, 4: 80}.get(count, 100)

def yjy(count):
    """
    影剧院
    2家以上100分；1家60分；没有0分
    :param count:
    :return:
    """
    return {0: 0, 1: 60}.get(count, 100)

def gj_1(count):


