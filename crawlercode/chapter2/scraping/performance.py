# -*- coding:utf-8 -*-

import re
from bs4 import BeautifulSoup
from commom import download
import lxml.html
import time


FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code',
          'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages',
          'neighbours')


def re_scraper(html):
    results = {}
    for field in FIELDS:
        results[field] = re.search('<tr id="places_{}__row">.*?<td class="w2p_fw">(.*?)</td>'.
                                   format(field), html).groups()[0]
        return results


def bs_scraper(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = {}
    for field in FIELDS:
        results[field] = soup.find('table').find('tr', id='places_{}__row'.format(field)).\
            find('td', class_='w2p_fw').text
        return results


def lxml_scraper(html):
    tree = lxml.html.fromstring(html)
    results = {}
    for field in FIELDS:
        results[field] = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content()
        return results


def main():
    num_iterations = 100   # number of times to test each scraper
    html = download('http://example.webscraping.com/places/default/view/China-47')
    for name, scraper in \
            [('Regular Expression', re_scraper), ('BeautifulSoup', bs_scraper), ('Lxml', lxml_scraper)]:
        # record start time of scrape
        start = time.time()
        for i in range(num_iterations):
            if scraper == re_scraper:
                re.purge()     # 正则表达式会缓存搜索结果，保证公平以清楚缓存
            result = scraper(html)
            # check scrapped result is as expected，assert()为断言函数，语句表示一定为真
            assert(result['area'] == '9,596,960 square kilometres')
        # record end time of scrape and output the total
        end = time.time()
        print '%s: %.2f seconds' % (name, end - start)


if __name__ == '__main__':
    main()







