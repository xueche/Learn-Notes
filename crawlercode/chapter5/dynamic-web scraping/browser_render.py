# -*- coding: utf-8 -*-

import csv
import time
from PySide.QtGui import QApplication
from PySide.QtCore import QEventLoop, QTimer
from PySide.QtWebKit import QWebView


class BrowserRender(QWebView):
    def __init__(self, display=True):
        self.app = QApplication([])
        QWebView.__init__(self)
        if display:
            self.show()    # show the browser

    def open(self, url, timeout=60):
        """wait for download to complete and return result"""
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)   # True表示触发定时器后，仅执行事件一次
        timer.timeout.connect(loop.quit)    # 若超时，则连接loop.quit,退出事件循环
        self.loadFinished.connect(loop.quit)
        self.load(url)
        timer.start(timeout * 1000)    # 定时器以ms为单位，设置超时时间为60s
        loop.exec_()      # 等待网页加载完成后，在执行后面的代码

        if timer.isActive():
            # downloaded successfully
            timer.stop()
            return self.html()
        else:
            # timed out
            print 'Request timed out:', url

    def html(self):
        """shortcut to return the current HTML"""
        return self.page().mainFrame().toHtml()

    def find(self, pattern):
        return self.page().mainFrame().findAllElements(pattern)

    def attr(self, pattern, name, value):
        for e in self.find(pattern):
            e.setAttribute(name, value)

    def text(self, pattern, value):
        for e in self.find(pattern):
            e.setPalintext(value)

    def click(self, pattern):
        for e in self.find(pattern):
            e.evaluateJavaScript("this.click()")

    def wait_load(self, pattern, timeout=60):
        """wait for this pattern to be found in webpage and return matches"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.app.processEvents()
            matches = self.find(pattern)
            if matches:
                return matches
        print 'wait load timed out'


def main():
    br = BrowserRender()
    br.open('http://example.webscraping.com/places/default/search')
    br.attr('#search_term', 'value', '.')
    br.text('#page_size option:checked', '1000')
    br.click('#search')
    br.app.exec_()

    elements = br.wait_load('#results a')
    writer = csv.writer(open('D:\countries1.csv', 'w',), lineterminator='\n')   # linerterminator='\n'避免隔行写入的问题
    for country in [e.toPlainText().strip() for e in elements]:
            writer.writerow([country])


if __name__ == '__main__':
    main()
