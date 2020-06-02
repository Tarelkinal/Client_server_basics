# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy_photo_hw6.building_materials_parser.items import BuildingMaterialsParserItem
from scrapy.loader import ItemLoader

class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, params):
        self.start_urls = [f"https://leroymerlin.ru/search/?q={params['key_word']}"]

    def parse(self, response: HtmlResponse):

        links = response.xpath('//a[@class="black-link product-name-inner"]/@href')
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

        next_button = response.xpath('//a[@navy-arrow="next"]/@href').extract_first()
        yield response.follow(next_button, callback=self.parse)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=BuildingMaterialsParserItem(), response=response)
        loader.add_xpath('title', '//h1/text()')
        loader.add_xpath('image', '//source[@media=" only screen and (min-width: 1024px)"]/@srcset')
        loader.add_xpath('price', '//meta[@itemprop="price"]/@content')
        loader.add_xpath('characteristic_name', '//dt[@class="def-list__term"]/text()')
        loader.add_xpath('characteristic_value', '//dd[@class="def-list__definition"]/text()')
        yield loader.load_item()

        # title = response.xpath('//h1/text()').extract_first()
        # image = response.xpath('//source[@media=" only screen and (min-width: 1024px)"]/@srcset').extract()
        # yield BuildingStaffParserItem(title=title, image=image)

