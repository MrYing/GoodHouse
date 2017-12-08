from pymongo import MongoClient
from scrapy.exceptions import DropItem

from GoodHouse.settings import MONGO_URI, MONGO_DATABASE
from GoodHouse.utils.lbs import LBS


class AMap(object):

    def open_spider(self, spider):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DATABASE]
        self.lbs = LBS()

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # if not item:
        #     raise DropItem('item Dropped!')
        if item.get('tag'):
            return item
        if 'room' in item['table']:
            return item
        if item.get('location'):
            return item

        return self.lbs.get_poi(item)