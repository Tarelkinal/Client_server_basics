from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from scrapy_hw5.booksparser import settings
from scrapy_hw5.booksparser.spiders.labirintru import LabirintruSpider
from scrapy_hw5.booksparser.spiders.book24ru import Book24ruSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(Book24ruSpider, topic='Толстой')
    process.crawl(LabirintruSpider, topic='Гоголь')
    process.start()


