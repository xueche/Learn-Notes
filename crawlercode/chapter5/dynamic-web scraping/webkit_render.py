# -*- coding: utf-8 -*-

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtWebKit import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtWebKit import *
import lxml.html
import downloader


def direct_download(url):
    download = downloader.Downloader()
    return download(url)


def webkit_download(url):
    app = QApplication([])    # 初始化QApplication对象，在其它Qt对象完成初始化之前，Qt框架需要先创建该对象
    webview = QWebView()      # 创建WebView对象，该对象是Web文档的容器
    webview.loadFinished.connect(app.quit)
    webview.load(url)     # 将要加载的URL传递给QWebView,PyQt需要将URL字符串封装在QUrl对象当中，对于Pyside是可选项
    app.exec_()   # delay here until download finished
    return webview.page().mainFrame().toHtml()


def parse(html):
    tree = lxml.html.fromstring(html)
    print tree.cssselect('#result')[0].text_content()


def main():
    url = 'http://example.webscraping.com/places/default/dynamic'
    parse(direct_download(url))
    parse(webkit_download(url))


if __name__ == '__main__':
    main()