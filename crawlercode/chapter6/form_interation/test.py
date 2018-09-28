# -*- coding: utf-8 -*-
import json
import urllib2
import cookielib
import urllib

#session_filename = 'D:\logins.json'
#json_data = json.loads(open(session_filename, 'rb').read())
#print json_data
#response = urllib2.urlopen('http://example.webscraping.com')
#print response.geturl()

filename = 'cookie.txt'
#声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
cookie = cookielib.MozillaCookieJar(filename)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
postdata = urllib.urlencode({
            'user_name': '2016282170023',
            'password': '19940712'
        })
#登录教务系统的URL
loginUrl = 'http://cas.whu.edu.cn/authserver/login'
#模拟登录，并把cookie保存到变量
result = opener.open(loginUrl, postdata)
#保存cookie到cookie.txt中
cookie.save(ignore_discard=True, ignore_expires=True)
#利用cookie请求访问另一个网址，此网址是成绩查询网址
gradeUrl = 'http://cas.whu.edu.cn/authserver/index.do'
#请求访问成绩查询网址
result = opener.open(gradeUrl)
print result.geturl()