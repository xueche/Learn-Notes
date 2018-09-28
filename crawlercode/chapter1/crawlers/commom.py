# -*- coding: utf-8 -*-

import urllib2
import urlparse


def download1(url):
    """Simple download"""
    return urllib2.urlopen(url).read()


def download2(url):
    """Download function that catch errors"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download Error:', e.reason
        html = None
    return html


def download3(url, retry=2):
    """Download function that catch errors, if the error is 5XX,retry twice"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download Error:', e.reason
        html = None
        if hasattr(e, 'code') and 500 <= e.code <= 600:
            if retry > 0:
                return download3(url, retry-1)
    return html


def download4(url, user_agent='wswp', retry=2):
    """Download function that includes user agent support"""
    print 'Downloading:', url
    headers = {'User_agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download Error:', e.reason
        html = None
        if hasattr(e, 'code') and 500 <= e.code <= 600:
            if retry > 0:
                return download4(url, user_agent, retry-1)
    return html


def download5(url, user_agent='wswp', proxy=None, retry=2):
    """Download function with support for proxies"""
    print 'Downloading:', url
    headers = {'User_agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        # 其中urlparse.urlparse(url).scheme表示得到网页的协议类型，例如http、HTTPS、ftp等等
        # proxy_params是一个字典，里面存放着代理的端口号，等同于proxy_params = {‘https', '127.0.0.1:1080'}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
        # 使用ProxyHandler类设置代理访问网页
    try:
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download Error:', e.reason
        html = None
        if hasattr(e, 'code') and 500 <= e.code <= 600:
            if retry > 0:
                return download5(url, user_agent, proxy, retry-1)
    return html


download = download5

if __name__ == '__main__':
    """make a script both importable and executable"""
    print download('http://example.webscraping.com')




