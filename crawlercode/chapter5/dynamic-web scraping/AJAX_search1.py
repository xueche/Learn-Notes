# -*- coding: utf-8 -*-

import json
import string
import downloader
import mongo_cache

FIELDS = ('areas', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone',
          'postal_code_format', 'postal_code_ regex', 'languages', 'neighbours')


def main():
    template_url = 'http://example.webscraping.com/places/ajax/search.json?&search_term={}&page_size=10&page={}'
    countries = set()     # 先将数据存储在集合中，因为集合这种数据类型不会存储重复的元素
    download = downloader.Downloader(mongo_cache.MongoCache())

    for letter in string.lowercase:    # 从a-z进行遍历搜索
        page = 0
        while True:
            html = download(template_url.format(letter, page))
            try:
                ajax = json.loads(html)    # 将JSON格式的数据使用json模块解析成一个字典
            except ValueError as e:
                print e
                ajax = None
            else:
                for record in ajax['records']:
                    # print record['country']
                    countries.add(record['country'])
            page += 1
            if ajax is None or page >= ajax['num_pages']:
                break

    open('D:\countries.txt', 'w').write('\n'.join(sorted(countries)))


if __name__ == '__main__':
    main()
    print 'done'


