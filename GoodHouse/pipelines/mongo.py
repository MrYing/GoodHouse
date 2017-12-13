import pymongo


class MongoPipeline(object):

    # collection_name = {
    #     'anjuke': 'anjuke',
    #     'anjuke_room': 'anjuke_room'
    # }

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
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        # for pictures
        if item.get('tag'):
            item.pop('tag')
            self.db[item.pop('table')].update_one(
                {'house_id': item.pop('house_id')},
                {'$addToSet': item},
                upsert=True
            )
        else:
            self.db[item.pop('table')].update_one(
                {'house_id': item.pop('house_id')},
                {'$set': item},
                upsert=True
            )
