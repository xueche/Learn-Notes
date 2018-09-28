# -*- coding: utf-8 -*-

import re
import csv
import lxml.html
from link_crawler import link_crawler


class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('D:\countries.csv', 'w'))  # 'w'表示写入模式，写入D盘countries文件中
        self.fields = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld',
                       'currency_code', 'currency_name', 'phone', 'postal_code_format',
                       'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_%s__row > td.w2p_fw' % field)
                [0].text_content())
            self.writer.writerow(row)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)', max_depth=1,
                 scrape_callback=ScrapeCallback())