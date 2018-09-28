# -*- coding: utf-8 -*-

import csv
# from zipfile import ZipFile
# from StringIO import StringIO
# from downloader import Downloader


def alexa():
    # D = Downloader()
    # zipped_data = D('http://s3.amazonaws.com/alexa-static/top-1m.csv.zip')   # 下载.zip文件
    urls = [] # top 1 million URL's will be stored in this list
    # with ZipFile(StringIO(zipped_data)) as zf:    # 下载得到的压缩文件需要进行StringIO封装后传给ZipFile,类似一个接口
        # csv_filename = zf.namelist()[0]           # 从.zip文件中提取CSV文件
    # 直接读取本地CSV文件
    for _, website in csv.reader(open('D:/top-1m.csv')):    # 解析并遍历CSV文件中的每一行，并抽出域名数据
        urls.append('http://' + website)
    return urls


if __name__ == '__main__':
    print len(alexa())