# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    origin_user_name = scrapy.Field()
    origin_user_id = scrapy.Field()
    user_name = scrapy.Field()
    photo = scrapy.Field()
    status = scrapy.Field()
