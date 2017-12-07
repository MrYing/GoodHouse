from random import choice

from GoodHouse.settings import AMAP_KEYS


class AMap(object):

    to_ip_url = 'http://restapi.amap.com/v3/geocode/geo?key={}&address={}&city={}'
    'http://restapi.amap.com/v3/place/around?key={}&location=116.456299,39.960767&radius=1000&types=商务写字楼'

    def process_item(self, item, spider):
        pass