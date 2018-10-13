import scrapy
from..items import Zufang1Item
class GanjiSpider(scrapy.Spider):
    name = "zufang"
    start_urls = ["http://bj.ganji.com/fang1/"]

    def parse(self, response):
        # print(response)
        zf = Zufang1Item()
        title_list = response.xpath(".//div[@class='f-list-item ershoufang-list']/dl/dd[1]/a/text()").extract()
        price_list = response.xpath(".//div[@class='f-list-item ershoufang-list']/dl/dd[5]/div[1]/span[1]/text()").extract()
        # for i,j in zip(title_list, price_list):
        #     print(i,":",j)
        for i,j in zip(title_list, price_list):
            zf['title'] = i
            zf['money'] = j
            yield zf