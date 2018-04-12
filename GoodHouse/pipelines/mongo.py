import pymongo


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.client.drop_database(self.mongo_db)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if 'new_data' in item:
            item.pop('new_data')
            self.db[item.pop('table')].insert_one(item)
        else:
            name, value = item.pop('item')
            self.db[item.pop('table')].update_one(
                {'house_id': item.pop('house_id')},
                {'$push': {name: {'$each': value}}},
                upsert=True
            )
