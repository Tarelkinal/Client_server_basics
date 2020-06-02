# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import hashlib
from scrapy.utils.python import to_bytes
import re


class BuildingStaffParserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.building_materials

    def process_item(self, item, spider):

        # из полей item characteristic_name и characteristic_value собираем словарь characteristics
        # числовые значения характеристик переводим в тип float

        item['characteristics'] = {}
        for i in range(len(item['characteristic_name'])):
            try:
                item['characteristics'].update(
                    {item['characteristic_name'][i]: float(re.sub(r'\s', '', item['characteristic_value'][i]))})
            except ValueError:
                item['characteristics'].update(
                    {item['characteristic_name'][i]: item['characteristic_value'][i]})
        item.pop('characteristic_name')
        item.pop('characteristic_value')
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class MaterialsImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['image']:
            for img in item['image']:
                try:

                    # передаем title, как мета данные запроса, чтобы потом использовать его в file_path

                    yield scrapy.Request(img, meta={'title': item['title']})
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['image'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None):

        # так как в эту функцию не передается item, то заголовок объявления передаем через метаданные запроса
        # новые путь строиться на основе заголовка объявления,
        # все фото с одного объявления будут лежать в одной папке с названием этого объялвения

        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f"files/{request.meta['title']}/{image_guid}.jpg"
