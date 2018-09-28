# -*- coding: utf-8 -*-

# try:
from PySide.QtGui import QApplication
from PySide.QtCore import QEventLoop, QUrl
from PySide.QtWebKit import QWebView
# except ImportError:
# from PyQt4.QtGui import QApplication
# from PyQt4.QtCore import QUrl, QEventLoop, QTimer
# from PyQt4.QtWebKit import QWebView
#  如果Pyside不可用，则会抛出ImportError异常，然后导入PyQt模块。如果PyQt模块也不可用，则会抛出另一个ImportError异常
# 浏览器渲染引擎WebKit，通过Qt框架获得该引擎的python接口
# Qt框架有两个可用的python库，PyQt和PySide
# WebKit用来执行JavaScript，然后访问生成的HTML。因此需要对浏览器渲染引擎进行扩展，使其能够支持交互功能
# 动态网站依赖于JavaScript,不再是加载后后立即下载所有页面内容，会造成许多网页在浏览器中展示的内容不会出现在HTML源代码中


def main():
    app = QApplication([])
    webview = QWebView()
    loop = QEventLoop()
    # 创建QEventLoop对象，该对象用于创建本地时间循环
    webview.loadFinished.connect(loop.quit)
    # QWebView对象的loadFinished回调连接了QEventLoop的quit方法，从而可以在网页加载完成之后停止事件循环
    webview.load(QUrl('http://example.webscraping.com/places/default/search'))
    loop.exec_()
    # QwebView的加载方法是异步的，执行过程会在网页加载时立即传入下一行，
    # 但我们希望等待网页加载完成，因此需要在事件循环启动时调用loop.exec_()

    webview.show()     # 调用QWebViewGUI的show()方法来显示渲染窗口，以方便调试
    frame = webview.page().mainFrame()     # 创建一个指代框架的变量
    # 使用CSS模式在框架中定位元素，然后设置搜索参数
    frame.findFirstElement('#search_term').setAttribute('Value', '.')
    frame.findFirstElement('#page_size option:checked').setPlainText('1000')
    # 使用evaluate JavaScript()方法提交事件，模拟点击事件
    frame.findFirstElement('#search').evaluateJavaScript('this.click()')
    app.exec_()  # 进入应用的事件循环，可以对表单操作进行复查，如果没有使用该方法，脚本就会直接结束

    # 等待结果，三种方法处理：
    # 1、等待一定时间，期望AJAX事件能够在此时刻之前完成
    # 2、重写Qt的网络管理器，跟踪URL请求完成的事件
    # 3、轮询网页，等待特定内容出现，下面采用第三种方法
    elements = None
    while not elements:
        app.processEvents()    # 用于给Qt事件循环执行任务的事件，比如响应点击事件和更新GUI
        elements = frame.findAllElements('#results a')
    countries = [e.toPlainText().strip() for e in elements]
    print countries


if __name__ == '__main__':
    main()


