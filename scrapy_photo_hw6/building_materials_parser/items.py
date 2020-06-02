# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader.processors import MapCompose, TakeFirst, Compose
import scrapy
import re


def clean_values(s):
    return re.findall(r'(\S+.*)\n', ''.join(s))


def to_float(s):
    return float(re.sub(r'\s+', '', s))


class BuildingMaterialsParserItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    image = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(to_float), output_processor=TakeFirst())
    characteristics = scrapy.Field()
    characteristic_name = scrapy.Field()
    characteristic_value = scrapy.Field(input_processor=Compose(clean_values))

