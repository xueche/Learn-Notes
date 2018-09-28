# -*- coding: utf-8 -*-

try:
    import cPickle as pickle
except ImportError:
    import pickle
import zlib
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.binary import Binary
from link_crawler import link_crawler


class MongoCache:
    def __init__(self, client=None, expires=timedelta(days=30)):
        """
        client: mongo database client
        expires: timedelta of amount of time before a cache entry is considered expired
        """
        # if a client object is not passed
        # then try connecting to mongodb at the default localhost port
        self.client = MongoClient('localhost', 27017) if client is None else client
        # create collection to store cached webpages,
        # which is the equivalent of a table in a relational database
        self.db = self.client.alexa     # 建立名字为alexa的数据库
        self.db.website.create_index('timestamp', expireAfterSeconds=expires.total_seconds())
        # 在alexa数据库建立名为website的collections

    def __contains__(self, url):
        try:
            self[url]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, url):
        """Load value at this URL"""
        record = self.db.website.find_one({'_id': url})
        if record:
            # return record['result']
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + 'does not exist')

    def __setitem__(self, url, result):
        """Save value for this URL"""
        # record = {'result':result, 'timestamp':datetime.now())
        record = {'result': Binary(zlib.compress(pickle.dumps(result))), 'timestamp': datetime.utcnow()}
        self.db.website.update({'_id': url}, {'$set': record}, upsert=True)  # mongodb 更新文档
        # print self.db.webpage.find_one({'_id': url})

    def clear(self):
        self.db.website.drop()


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/places/default/(index|view)', cache=MongoCache())
