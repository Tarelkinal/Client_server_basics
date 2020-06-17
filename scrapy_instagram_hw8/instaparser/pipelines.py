# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from hashlib import sha1
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from scrapy.utils.python import to_bytes


class InstaparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        item['_id'] = sha1(str(item).encode('utf-8')).hexdigest()

        collection = self.mongo_base[spider.name]

        if not collection.find({'_id': item['_id']}).count():
            collection.insert_one(item)
        return item


class InstaparserImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['photo']:
            try:

                # передаем user_name, как мета данные запроса, чтобы потом использовать его в file_path

                yield scrapy.Request(item['photo'], meta={'user_name': item['user_name']})
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):

        # так как в эту функцию не передается item, то заголовок объявления передаем через метаданные запроса
        # новые путь строиться на основе заголовка объявления,
        # все фото с одного объявления будут лежать в одной папке с названием этого объялвения

        image_guid = sha1(to_bytes(request.url)).hexdigest()
        return f"files/{request.meta['user_name']}/{image_guid}.jpg"