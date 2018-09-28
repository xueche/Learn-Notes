# -*- coding: utf-8 -*-

import urllib2
import lxml.html


def scrape(html):
    tree = lxml.html.fromstring(html)  # 将有可能不合法的HTML解析为统一的格式，不会额外添加<html>和<body>标签
    td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]  # 使用CSS选择器定位需要抓取的数据,
    # 选择 ID=‘places_area_row'的<tr>行标签下class='wap_fw'的<td>列标签
    area = td.text_content()     # 抓起所需要的数据
    return area


if __name__ == '__main__':
    html = urllib2.urlopen('http://example.webscraping.com/places/default/view/China-47').read()
    print scrape(html)