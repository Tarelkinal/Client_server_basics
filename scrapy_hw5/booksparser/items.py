# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksparserItem(scrapy.Item):
    _id = scrapy.Field()
    link = scrapy.Field()
    name = scrapy.Field()
    authors = scrapy.Field()
    price_old = scrapy.Field()
    price_new = scrapy.Field()
    rate = scrapy.Field()
