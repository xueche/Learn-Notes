# -*- coding: utf-8 -*-

import urllib
import urllib2
import mechanize
import login

COUNTRY_URL = 'http://example.webscraping.com/places/default/edit/United-Kingdom-239'


def edit_country():
    opener = login.login_cookies()
    country_html = opener.open(COUNTRY_URL).read()
    data = login.parse_form(country_html)
    import pprint; pprint.pprint(data)
    print 'Population before: ' + data['population']
    data['population'] = int(data['population']) + 1
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(COUNTRY_URL, encoded_data)
    opener.open(request)

    country_html = opener.open(COUNTRY_URL).read()
    data = login.parse_form(country_html)
    print 'Population after:', data['population']


def mechanize_edit():
    """use mechanize to increment population"""
    # login
    br = mechanize.Browser()    # 创建一个Mechanize浏览器对象
    br.open(login.LOGIN_URL)
    br.select_form(nr=0)       # 选择登录表单
    print br.form
    br['email'] = login.LOGIN_EMAIL
    br['password'] = login.LOGIN_PASSWORD
    response = br.submit()
    print response.geturl()

    # edit country
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population before:', br['population']
    br['population'] = str(int(br['population']) + 1)
    br.submit()

    # check country
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population after:', br['population']


if __name__ == '__main__':
    #edit_country()
    mechanize_edit()
