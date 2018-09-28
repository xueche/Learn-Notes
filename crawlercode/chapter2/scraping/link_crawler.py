# -*- coding: utf-8 -*-

import robotparser
import Queue
import re
import urlparse
from datetime import datetime
import time
import urllib2


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp',
                 proxy=None, num_retries=1, scrape_callback=None):
    """Crawl from the given seed URL following links matched by link_regex"""
    # the queue of URL's that still to be crawled
    crawl_queue = Queue.deque([seed_url])
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}
    # track how many URL's have been download
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or{}
    if user_agent:
        headers['user_agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        # check url passes robot.txt restrictions
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []
            if scrape_callback:      # 回调函数，在发生某个特定事件之后调用该函数，即在网页下载完成后调用该函数
                links.extend(scrape_callback(url, html) or [])

            depth = seen[url]     # 只关注于首页抓取的深度
            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached download maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url


class Throttle:
    """Throttle downloading by sleeping between requests to same domain"""
    def __init__(self, delay):    # 定义类中的初始函数__init__，self是必需参数，表示类实例本身,无需传入该参数
        # amount of delay between downloading for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domain = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc   # 返回url的服务器地址（）netloc
        last_accessed = self.domain.get(domain)  # get()函数返回字典中指定键的数值

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                # domain has been accessed recently, so need to sleep
                time.sleep(sleep_secs)
        # update the last accessed time
        self.domain[domain] = datetime.now()


def download(url, headers, proxy, num_retries, data=None):
    print 'Downloading:', url
    request = urllib2.Request(url, data, headers)
    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        response = opener.open(request)
        html = response.read()
        code = response.code
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code <= 600:
                return download(url, headers, proxy, data, num_retries-1)
        else:
            code = None
    # print code
    return html


def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain"""
    link, _ = urlparse.urldefrag(link)  # remove hash to avoid duplicate
    return urlparse.urljoin(seed_url, link)


def same_domain(url1, url2):
    """Return True if both URL's belong to same domain"""
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def get_robots(url):
    """Initialize robots parser for this domain"""
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp


def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


if __name__ == '__main__':
    # link_crawler('http://example.webscraping.com', '/places/default/(view|index)', delay=2, user_agent='BadCrawler',
    #             num_retries=1)
    link_crawler('http://example.webscraping.com', '/places/default/(index|view)', delay=5, num_retries=1, max_depth=1,
                 user_agent='GoodCrawler')

