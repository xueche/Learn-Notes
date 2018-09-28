# -*- coding: utf-8 -*-

import re
# import urlparse
from commom import download


def link_crawler(seed_url, link_regex):
    """Crawl from the given seed url following links matched by link_regex"""
    crawl_queue = [seed_url]   # 新建一个列表
    print crawl_queue
    while crawl_queue:
        url = crawl_queue.pop()   # 移除列表后一个元素，并返回该元素
        html = download(url)
        # print crawl_queues
        """filter for links matching our regular expression"""
        for link in get_links(html):
            if re.match(link_regex, link):
                # add this link to crawl queue
                # link = urlparse.urljoin(seed_url, link)   # form absolute link
                crawl_queue.append(link)
                # print crawl_queue


def get_links(html):
    """return a list link from html"""
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    # print webpage_regex.findall(html)
    return webpage_regex.findall(html)


if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)')
