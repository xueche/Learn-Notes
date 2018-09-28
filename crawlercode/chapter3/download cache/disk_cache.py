# -*- coding: utf:8 -*-

import os
import re
import urlparse
import shutil
import zlib
from datetime import datetime, timedelta
try:
    import cPickle as pickle
except ImportError:
    import pickle
from link_crawler import link_crawler


class DiskCache:
    def __init__(self, cache_dir='cache data', expires=timedelta(days=30), compress=True):
        """
        cache_dir: the root level folder for the cache
        expires:timedelta of amount of time"before a cache entry is considered expired
        compress:whether to compress data in the cache
        """
        self.cache_dir = cache_dir
        self.expires = expires
        self.compress = compress

    def url_to_path(self, url):
        """create file system path for this url"""
        components = urlparse.urlsplit(url)
        # when empty path set to /index.html
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        elif path.endswith('index'):      # 解决了IOError错误！！！
            path += '.html'
        filename = components.netloc + path + components.query
        # replace invalid characters
        filename = re.sub('[^/0-9a-zA-Z\-.,;_]', '_', filename)
        # restrict maximum number of characters
        filename = '\\'.join(segment[:255] for segment in filename.split('/'))  # 以‘/‘连接每个segment
        return os.path.join(self.cache_dir, filename)  # 将这两个路径组合返回

    def __getitem__(self, url):
        """load data from disk for this url"""
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:   # open函数中路径必须是目录名+文件名
                data = fp.read()     # 读取文件中存储的数据
                if self.compress:
                    data = zlib.decompress(data)
                result, timestamp = pickle.loads(data)  # pickle对读取后的数据进行反序列化
                if self.has_expired(timestamp):
                    raise KeyError(url + 'has expired')  # 如果引发异常，后面的代码将不能执行
                return result
        else:
            # URL has not yet been cached
            raise KeyError(url + 'does not exist')

    def __setitem__(self, url, result):
        """save data to disk for this url"""
        path = self.url_to_path(url)
        folder = os.path.dirname(path)  # 获取文件路径所在的目录
        if not os.path.exists(folder):
            os.makedirs(folder)

        data = pickle.dumps((result, datetime.utcnow()))
        # pickle模块可以序列化对象并保存到磁盘中
        if self.compress:
            data = zlib.compress(data)
        with open(path, 'wb') as fp:
            fp.write(data)

    def __delitem__(self, url):
        """Remove the value at this key and any empty parent sub-directories
        """
        path = self._key_path(url)
        try:
            os.remove(path)
            os.removedirs(os.path.dirname(path))
        except OSError:
            pass

    def has_expired(self, timestamp):
        """Return whether this timestamp has expired"""
        return datetime.utcnow() > timestamp + self.expires

    def clear(self):
        """remove all the cache values"""
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/places/default/(index|view)', cache=DiskCache())





