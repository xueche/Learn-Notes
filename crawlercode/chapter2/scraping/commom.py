# -*- coding: utf-8 -*-

import urllib2


def download(url, user_agent=None):
    print 'Downloading:', url
    headers = {'user_agent': user_agent or 'wswp'}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download Error:', e.reason
        html = None
    return html


if __name__ == '__main__':
    download('http://example.webscraping.com')
