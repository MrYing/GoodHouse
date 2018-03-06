"""
get pois by gaodeAPI
"""
import time
import logging
import asyncio
from random import choice
from operator import itemgetter

import aiohttp
from pymongo import MongoClient
from bson.objectid import ObjectId

from GoodHouse.settings import AMAP_KEYS, MONGO_DATABASE, MONGO_URI

logging.basicConfig(
    level=logging.INFO
)


class LBS:

    logger = logging.getLogger('LBS')

    to_ip_url = 'http://restapi.amap.com/v3/geocode/geo?key={}&address={}'
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
        {'code': '010100|010200|010300', 'name': 'gas', 'radius': 500},
        {'code': '071900', 'name': 'funeral_parlor', 'radius': 5000},
        {'code': '110101|110102|110103|110104', 'name': 'park', 'radius': 2000},
        {'code': '110105|110106', 'name': 'square', 'radius': 2000},
        {'code': '190204|190205', 'name': 'water_system', 'radius': 2000},
        {'code': '110200', 'name': 'scenic_area', 'radius': 2000},
    ]

    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DATABASE]

    semaphore = asyncio.Semaphore(100)

    async def fetch(self, url):
        try:
            with (await self.semaphore):
                async with aiohttp.ClientSession() as s:
                    async with s.get(url, timeout=60) as r:
                        return await r.json()
        except:
            pass

    async def get_poi(self, address, house_id, collection):
        url = self.to_ip_url.format(choice(AMAP_KEYS), address)
        result = await self.fetch(url)

        if not result:
            return

        if int(result.get('count', 0)) == 0:
            self.logger.error('can not find ip %s', url)
            return

        self.logger.info('get ip! %s', url)
        result = result['geocodes'][0]

        item = {
            'formatted_address': result['formatted_address'],
            'province': result['province'],
            'district': result['district'],
            'location': result['location']
        }

        poi_result = {}
        for poi in self.pois:
            url = self.to_poi_url.format(
                choice(AMAP_KEYS), item['location'], poi['radius'], poi['code']
            )
            poi_data = await self.fetch(url)
            # if int(poi_data.get('infocode', 0)) != 10000:
            #     self.logger.error('can not find pois %s', url)
            #     poi_result[poi['name']] = []
            #     continue
            if not poi_data:
                continue

            poi_result[poi['name']] = self.sort_pois(poi_data.get('pois', []))

        self.logger.info('get pois! %s', poi_result)
        # return item.update({'pois': poi_result})
        item.update({'pois': poi_result})
        collection.update_one(
            {'_id': ObjectId(house_id)},
            {'$set': item}
        )
        self.logger.info('update %s', item)

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

    def get_address(self, collection):
        for house in collection.find(
                {'pois': {'$exists': 0}, 'address': {'$exists': 1}},
                {'city': 1, 'address': 1, 'name': 1}
        ):
            address = house['city'] + house['address'] + house['name']
            yield address, ObjectId(house['_id'])

    # def store(self, house_id, address, collection):
    #     item = self.get_poi(address)
    #     collection.update_one(
    #         {'_id': house_id},
    #         {'$set': item}
    #     )
    # def store(self, item, house_id, collection):
    #     collection.update_one(
    #         {'_id': ObjectId(house_id)},
    #         {'$set': item}
    #     )
    #     self.logger.info('update %s', item)

    def store_pois(self, collection_name):
        collection = self.db[collection_name]
        loop = asyncio.get_event_loop()
        # tasks = [
        #     self.store(house_id, address, collection)
        #     for house_id, address in self.get_address(collection)
        # ]
        # house_ids, tasks = [], []
        # for house_id, address in self.get_address(collection):
        #     house_ids.append(house_id)
        #     tasks.append(self.get_poi(address))
        tasks = [
            self.get_poi(address, house_id, collection)
            for address, house_id in self.get_address(collection)
        ]

        loop.run_until_complete(asyncio.gather(*tasks))
        # for house_id, item in zip(house_ids, items):
        #     self.store(item, house_id, collection)

        # loop.close()
        # self.client.close()


if __name__ == '__main__':
    # lbs = LBS()
    # lbs.store_pois('anjuke')
    while True:
        # time.sleep(5*60)
        LBS().store_pois('anjuke')
        # LBS().store_pois('souhujiaodian')
        time.sleep(30 * 60)