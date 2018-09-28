# -*- coding: utf-8 -*-

import re
import urlparse
from commom import download


def link_crawler(seed_url, link_regex):
    crawl_queue = [seed_url]
    seen = set(crawl_queue)   # keep track which URL's have seen before,创建一个集合
    # print seen
    while crawl_queue:
        url = crawl_queue.pop()
        html = download(url)
        for link in get_links(html):
            # print link
            if re.match(link_regex, link):
                # print 'success'
                link = urlparse.urljoin(seed_url, link)
                if link not in seen:     # check if have already seen this link
                    seen.add(link)
                    crawl_queue.append(link)
            # else:
                # print 'fail'


def get_links(html):
    web_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # print web_regex.findall(html)
    return web_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)')