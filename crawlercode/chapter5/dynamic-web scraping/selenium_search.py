# -*- coding: utf-8 -*-

from selenium import webdriver
import csv


def main():
    driver = webdriver.Firefox()    # 创建一个到浏览器的连接,需要配置浏览的Selenium IDE 和环境变量
    driver.get('http://example.webscraping.com/places/default/search')  # 在选定的浏览器中加载网页
    driver.find_element_by_id('search_term').send_keys('.')      # 定位到搜索文本框并模拟键盘输入搜索条件
    # 使用JavaScript语句直接设置选项框的内容，以绕过selenium的限制
    driver.execute_script("document.getElementById('page_size').options[1].text='1000'")
    driver.find_element_by_id('search').click()   # 模拟网页点击search按钮
    driver.implicitly_wait(30)  # 设置30s的延时，如果要查找的元素没有出现，selenium至多等待30s,然后抛出异常
    links = driver.find_elements_by_css_selector('#results a')
    # print links
    countries = [link.text for link in links]
    writer = csv.writer(open('D:\countries2.csv', 'w',), lineterminator='\n')
    for country in countries:
        print country
        writer.writerow([country])       # 在写入csv中时，需要加[],将字符串写入同一个表格中
    print countries[0]
    driver.close()


if __name__ == '__main__':
    main()
