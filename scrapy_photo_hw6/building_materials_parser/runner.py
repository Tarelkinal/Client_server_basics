from scrapy.crawler import Settings
from scrapy.crawler import CrawlerProcess

from scrapy_photo_hw6.building_materials_parser import settings
from scrapy_photo_hw6.building_materials_parser.spiders.leroymerlinru import LeroymerlinruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    params = {'key_word': 'шпаклевка'}
    process.crawl(LeroymerlinruSpider, params=params)
    process.start()
