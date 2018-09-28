# -*- coding: utf-8 -*-

import json
import csv
import downloader

FIELDS = ('areas', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone',
          'postal_code_format', 'postal_code_ regex', 'languages', 'neighbours')


def main():
    writer = csv.writer(open('D:\countries.csv', 'w'))
    writer.writerow(FIELDS)
    D = downloader.Downloader()
    html = D('http://example.webscraping.com/places/ajax/search.json?&search_term=.&page_size=1000&page=0')
    ajax = json.loads(html)
    print ajax
    for record in ajax['records']:
        # row = [record[field] for field in FIELDS]
        writer.writerow([record['country']])


if __name__ == '__main__':
    main()
    print 'done'

