# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy_hw5.booksparser.items import BooksparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']

    def __init__(self, topic):
        self.start_urls = [f'https://www.labirint.ru/search/{topic}/?stype=0']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//a[@class="product-title-link"]/@href').extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        next_page = response.xpath('//a[@class="pagination-next__text"]/@href').extract_first()
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath('//h1/text()').extract_first()
        authors = response.xpath('//div[@class="authors"][1]/a/text()').extract_first()
        price_old = response.xpath('//span[@class="buying-priceold-val-number"]/text()').extract_first()
        price_new = response.xpath('//span[@class="buying-pricenew-val-number"]/text()').extract_first()
        rate = response.xpath('//div[@id="rate"]/text()').extract_first()
        yield BooksparserItem(link=link, name=name, authors=authors, price_old=price_old, price_new=price_new, rate=rate)
