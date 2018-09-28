# -*- coding: utf-8 -*-

import urllib
import urllib2
import glob
import os
import cookielib
import json
import time
import lxml.html
import pprint

LOGIN_EMAIL = '18226144@qq.com'
LOGIN_PASSWORD = '111111'
LOGIN_URL = 'http://example.webscraping.com/places/default/user/login'
URL = 'http://example.webscraping.com'
COUNTRY_URL = 'http://example.webscraping.com/places/default/edit/United-Kingdom-239'


def login_basic():
    """fails bacause not using formkey"""
    data = {'email': LOGIN_EMAIL, 'password': LOGIN_PASSWORD}
    encoded_data = urllib.urlencode(data)    # 设置表单中数据提交的编码为urlencode类型
    request = urllib2.Request(LOGIN_URL, encoded_data)  # 向指定URL提交表单,请求访问
    response = urllib2.urlopen(request)
    print response.geturl()


def login_formkey():
    """fails because not using cookies to match formkey"""
    html = urllib2.urlopen(LOGIN_URL).read()   # 下载指定网页的html源码
    data = parse_form(html)    # 提取表单中所有input标签的详情
    # pprint.pprint(data)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    # print data
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = urllib2.urlopen(request)
    print response.geturl()


def login_cookies():
    """working login"""
    cj = cookielib.CookieJar()    # 声明一个CookieJar对象实例来保存cookie
    # 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
    handler = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(handler)    # 通过handler来构建opener
    html = opener.open(LOGIN_URL).read()
    # print cj
    data = parse_form(html)
    # pprint.pprint(data)     #  pprint格式化输出python各种数据类型
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    # print data
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = opener.open(request)     # 需要使用HTTPCookieProcessor支持的opener打开请求网页，不能使用urllib2.urlopen()
    print response.geturl()
    return opener


def login_firefox():
    """load cookies form firefox"""
    session_filename = 'D:\logins.json'
    # print session_filename
    cj = load_ff_sessions(session_filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(URL).read()

    tree = lxml.html.fromstring(html)
    print tree.cssselect('ul#navbar li a')[0].text_content()
    return opener


def parse_form(html):
    """extract all input properties from the form"""
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data


def load_ff_sessions(session_filename):
    cj = cookielib.CookieJar()
    if os.path.exists(session_filename):
        try:
            json_data = json.loads(open(session_filename, 'rb').read())
        except ValueError as e:
            print 'Error parsing session JSON:', str(e)
        else:
            for window in json_data.get('windows', []):
                for cookie in window.get('cookies', []):
                    import pprint; pprint.pprint(cookie)
                    c = cookielib.Cookie(0, cookie.get('name', ''),
                                         cookie.get('value', ''),
                                         None, False,
                                         cookie.get('host', ''),
                                         cookie.get('host', '').startswith('.'),
                                         cookie.get('host', '').startswith('.'),
                                         cookie.get('path', ''), False,
                                         False, str(int(time.time()) + 3600 * 24 * 7), False,
                                         None, None, {})
                    cj.set_cookie(c)
    else:
        print 'Session filename does not exist:', session_filename
    return cj


def find_ff_sessions():
    paths = [
        '~/.mozilla/firefox/*.default',
        '~/Library/Application Support/Firefox/Profiles/*.default',
        '%APPDATA%/Roaming/Mozilla/Firefox/Profiles/*.default'
    ]
    for path in paths:
        filename = os.path.join(path, 'sessionstore.js')
        matches = glob.glob(os.path.expanduser(filename))   # glob模块会返回指定路径中所有匹配的文件
        # expanduser: 把path中包含的"~"和"~user"转换成用户目录
        # print matches
        if matches:
            return matches[0]


if __name__ == '__main__':
    #login_basic()
    #login_formkey()
    login_cookies()
    login_firefox()


