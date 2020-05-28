from lxml import html
import requests
from pymongo import MongoClient
import re
from datetime import datetime, timedelta
from hashlib import sha1


class Parser:

    def __init__(self, db_name='news_database', collection_name='news', news_list=None):
        self.header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                     '(KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'}
        self.db = MongoClient('localhost', 27017)[db_name]
        self.collection_name = collection_name
        self.news_list = news_list

    def add_data_into_db(self) -> None:

        # метод добавляет все записи, полученные при парсинге в бд, и выводит на печать их количество

        try:
            self.db[self.collection_name].insert_many(self.news_list)
            print('collection {} update: {} news were inserted '.format(self.collection_name,
                                                                             len(self.news_list)))
        except TypeError:
            print('{}: there are no data to insert'.format(__name__))

    def _request(self, link):
        response = requests.get(link, headers=self.header)
        assert response.ok, [response.status_code, link]
        return html.fromstring(response.text)

    @staticmethod
    def _add_id(li):

        # метод добавляет ключ _id в словарь новости

        for elem in li:
            elem['_id'] = sha1(str(elem).encode('utf-8')).hexdigest()
        return li

    def add_new_data_into_db(self) -> None:

        # метод добавляет только новые записи, полученные при парсинге в бд, и выводит на печать их количество
        # реализована обработка исключения в случае, если метод вызван, когда key_words не заданы

        try:
            i = 0
            for elem in self.news_list:
                if not self.db[self.collection_name].find(
                        {'_id': elem['_id']}).count():
                    self.db[self.collection_name].insert_one(elem)
                    i += 1
            print('Collection {} update: {}/{} vacancies were inserted '.format(self.collection_name,
                                                                                i, len(self.news_list)))
        except TypeError:
            print('{}: there are no data to add'.format(__name__))


class LentaRu(Parser):

    def __init__(self, db_name='news_database', collection_name='news'):
        super().__init__(db_name, collection_name)
        self.home_link = 'https://lenta.ru'
        self.news_list = self.get_news()

    def get_news(self):
        # парсим главные новости
        blocks = self._request(self.home_link).xpath('//div[@class="b-yellow-box__wrap"]'
                                                     '/div[@class="item"]/a[not(@class="b-link-external")]')
        li = [{'source': 'Lenta.Ru',
               'news_title': block.xpath('./text()')[0],
               'link': self.home_link + block.xpath('./@href')[0],
               'date': self._request(self.home_link + block.xpath('./@href')[0]).xpath(
                   '//div[@class="b-topic__header js-topic__header"]//time/@datetime')[0]} for block in blocks]
        li = self._add_id(li)
        return li


class MailNews(Parser):

    def __init__(self, db_name='news_database', collection_name='news'):
        super().__init__(db_name, collection_name)
        self.home_link = 'https://news.mail.ru'
        self.news_list = self.get_news()

    def get_news(self):

        # парсим все новости на странице

        blocks = self._request(self.home_link).xpath('//li[contains(@class, "list__item")]')
        li = []

        for block in blocks:
            link_2 = self._request(block.xpath('.//a/@href')[0]) if block.xpath('.//a/@href')[0].startswith('http') \
                else self._request(self.home_link + block.xpath('.//a/@href')[0])
            try:
                li.append({'source': link_2.xpath('//a[@class="link color_gray breadcrumbs__link"]//text()')[0] if len(link_2.xpath('//a[@class="link color_gray breadcrumbs__link"]/@href')) else link_2.xpath('//span[@class="note"]/span[not(contains(@class, "note__text"))]//text()')[0],
                           'news_title': block.xpath('.//child::text()')[0],
                           'link': self.home_link + block.xpath('.//a/@href')[0],
                           'date': link_2.xpath('//span[@class="note__text breadcrumbs__text js-ago"]/@datetime')[0]})
            except IndexError:
                print(block.xpath('.//a/@href')[0])
        li = self._add_id(li)
        return li


class YandexNews(Parser):

    def __init__(self, db_name='news_database', collection_name='news'):
        super().__init__(db_name, collection_name)
        self.home_link = 'https://yandex.ru'
        self.news_list = self.get_news()

    @staticmethod
    def __data(block):

        # метод для получения даты публикации и названия источника

        data = {'date': None, 'source': None}
        if re.search(r'в\s\d\d:\d\d', block.xpath('.//div[@class="story__info"]//text()')[0]):
            if re.search(r'вчера\sв', block.xpath('.//div[@class="story__info"]//text()')[0]):
                data['date'] = (datetime.today() + timedelta(-1)).strftime('%Y-%m-%d') + 'T' + \
                       re.findall(r'\d\d:\d\d', block.xpath('.//div[@class="story__info"]//text()')[0])[0] + ':00+03:00'
                data['source'] = re.findall(r'(.+)\sвчера\sв', block.xpath('.//div[@class="story__info"]//text()')[0])[
                    0]
            else:
                data['source'] = re.findall(r'(.+)\s\d+\s\w+\sв', block.xpath('.//div[@class="story__info"]//text()')[0])[
                    0]
        else:
            data['date'] = datetime.today().strftime('%Y-%m-%d') + 'T' + \
                   re.findall(r'\d\d:\d\d', block.xpath('.//div[@class="story__info"]//text()')[0])[0] + ':00+03:00'
            data['source'] = re.findall(r'(.+)\s\d\d:\d\d', block.xpath('.//div[@class="story__info"]//text()')[0])[0]
        return data

    def get_news(self):

        # парсим все новости на странице

        blocks = self._request(self.home_link + '/news').xpath('//div[@class="story__content"]'
                                                               '|//td[@class="stories-set__item"]')
        li = []

        for block in blocks:

            li.append({'source': self.__data(block)['source'],
                       'news_title': block.xpath('.//h2[@class="story__title"]//child::text()')[0],
                       'link': re.findall(r'(.+)\?', self.home_link + block.xpath('.//h2[@class="story__title"]//@href')[0])[0],
                       'date': self.__data(block)['date']})
        li = self._add_id(li)
        return li


if __name__ == '__main__':

    news_1 = LentaRu()

    news_1.add_data_into_db()

    news_2 = MailNews()

    news_2.add_data_into_db()

    news_3 = YandexNews()

    news_3.add_data_into_db()
