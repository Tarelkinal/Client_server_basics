# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
import re


class BooksparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.books

    def process_item(self, item, spider):
        item['price_old'] = int(re.findall(r'\w+', item['price_old'])[0]) if item['price_old'] is not None else None
        item['price_new'] = int(item['price_new']) if item['price_new'] is not None else None
        item['rate'] = float(re.sub(r',', '.', item['rate'])) if item['rate'] is not None else None
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
