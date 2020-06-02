# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy_hw5.booksparser.items import BooksparserItem


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']

    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 0
    }

    def __init__(self, topic):
        self.start_urls = [f'https://book24.ru/search/?q={topic}']

    def parse(self, response: HtmlResponse):
        book_links = response.xpath('//a[@class="book__title-link js-item-element ddl_product_link "]/@href').extract()
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)

        next_page = response.xpath('//a[@class="catalog-pagination__item _text js-pagination-catalog-item"]/@href').extract_first()
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        link = response.url
        name = response.xpath('//h1[@class="item-detail__title"]/text()').extract_first()
        authors = response.xpath('//a[@class="item-tab__chars-link"]/text()').extract_first()
        price_old = response.xpath('//div[@class="item-actions__price-old"]/text()').extract_first()
        price_new = response.xpath('//div[@class="item-actions__price"]/b/text()').extract_first()
        rate = response.xpath('//span[@class="rating__rate-value"]/text()').extract_first()
        yield BooksparserItem(link=link, name=name, authors=authors, price_old=price_old, price_new=price_new,
                              rate=rate)

