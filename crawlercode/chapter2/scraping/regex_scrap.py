# -*- coding: utf-8 -*-

import re
from commom import download


def scrape(url):
    html = download(url)
    area = re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)[0]
    return area


if __name__ == '__main__':
    print scrape('http://example.webscraping.com/places/default/view/China-47')