# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

class Zufang1Pipeline(object):
    def open_spider(self,spider):         #定义爬虫开始
     self.con = sqlite3.connect("zufang.sqlite")
     self.cu = self.con.cursor()          #爬虫开始与建立的数据库文件连接


    def process_item(self, item, spider):
        print(spider.name, 'pipelines')
        insert_sql = "insert into main.zufang (title, money) values('{}', '{}')".format(item['title'], item['money'])
        # 定义一个插入语句，format格式化数据,注意表格名为main.zufang
        print(insert_sql)         #通过打印来检测定义的插入语句是否正确
        self.cu.execute(insert_sql)     # 执行插入语句
        self.con.commit()      #提交数据，否则不会插入到数据库中
        return item


    def spider_close(self, spider):
         self.con.close()       #爬虫结束后关闭数据库