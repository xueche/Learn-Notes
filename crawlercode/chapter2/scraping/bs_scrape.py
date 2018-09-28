# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2


def scrape(url):
    soup = BeautifulSoup(url)    # 将有可能不合法的HTML解析为统一格式
    tr = soup.find(attrs={'id': 'places_area__row'})  # locate the area row
    td = tr.find(attrs={'class': 'w2p_fw'})      # locate the area tag
    area = td.text   # extract the text from this tag
    return area


if __name__ == '__main__':
    html = urllib2.urlopen('http://example.webscraping.com/places/default/view/China-47').read()
    print scrape(html)
