import requests
from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
import json
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class VacancyParser:

    def __init__(self, key_words=None, count_pages_to_parse=None):

        self.vacancy = key_words  # key_words могут быть не переданы при инициализации,
        # если класс планируется использовать только для работы с бд (парсинг не требуется)

        self.db = MongoClient('localhost', 27017)['vacancy_database']

        self.vacancy_list = self.get_vacancy_list(count_pages_to_parse) if self.vacancy is not None else None
        # при инициализации класса с переданным ключевым словом автоматически происходит парсинг

        self.collection_name = self._prepare_collection_name() if self.vacancy is not None else None

    @staticmethod
    def _salary_range(string) -> dict:

        # функция парсит информацию о зарплате на категории

        if string.startswith('от'):
            salary = {'min': int(''.join(re.findall(r'от\s(\d+)\s(\d*)', string)[0])),
                      'max': None}
        elif string.startswith('до'):
            salary = {'min': None,
                      'max': int(''.join(re.findall(r'до\s(\d+)\s(\d*)', string)[0]))}
        elif re.search(r'[-—]', string):
            salary = {'min': int(''.join(re.findall(r'(\d+)\s*(\d*)\s*[-—]', string)[0])),
                      'max': int(''.join(re.findall(r'[-—]\s*(\d+)\s(\d*)', string)[0]))}
        else:
            salary = {'min': int(''.join(re.findall(r'(\d+)\s(\d*)', string)[0])),
                      'max': int(''.join(re.findall(r'(\d+)\s(\d*)', string)[0]))}
        salary['currency'] = re.findall(r'\s(\w+)\.*$', string)[0]
        return salary

    def get_vacancy_list(self, num_pages_to_parse) -> list:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                 '(KHTML, like Gecko) Chrome/81.0.4044.113 YaBrowser/20.4.1.225 Yowser/2.5 Safari/537.36'}

        service = 'https://hh.ru'
        service_2 = 'https://www.superjob.ru'

        # парсинг для https://hh.ru
        li = []
        i = 0
        while i < num_pages_to_parse if num_pages_to_parse is not None else True:  # парсим заданное количество страниц или все, если не задано
            request = f'{service}/search/vacancy?area=1&text={self.vacancy}&page={i}'
            resp = requests.get(request, headers=headers)
            if not resp.ok:
                print(service, 'status_code:', resp.status_code)
                break
            soup = BeautifulSoup(resp.text, 'lxml')
            li.extend(soup.find_all(class_="vacancy-serp-item__row vacancy-serp-item__row_header"))
            if not soup.find('a', class_="bloko-button HH-Pager-Controls-Next HH-Pager-Control"):
                break
            i += 1

        # Блок для настройки регулярных выражений в функции _salary_range

        # for elem in li:
        #     if elem.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}) is not None:
        #         try:
        #             _salary_range(elem.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}).text)
        #         except IndexError:
        #             pprint(elem.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}).text)

        res = [{'vacancy_name': elem.find(class_="bloko-link HH-LinkModifier").text,
                'link': elem.find(class_="bloko-link HH-LinkModifier").attrs['href'],
                'salary': self._salary_range(
                    elem.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}).text) if elem.find('span', {
                    'data-qa': "vacancy-serp__vacancy-compensation"}) is not None else None,
                'service': service} for elem in li]

        # парсинг для https://www.superjob.ru
        li = []
        i = 1
        while i < num_pages_to_parse + 1 if num_pages_to_parse is not None else True:
            request = f'{service_2}/vacancy/search/'
            params = {'keywords': self.vacancy, 'page': i}
            resp = requests.get(request, headers=headers, params=params)
            if not resp.ok:
                print(service_2, 'status_code:', resp.status_code)
                break
            soup = BeautifulSoup(resp.text, 'lxml')
            li.extend(soup.find_all(class_="jNMYr GPKTZ _1tH7S"))
            if not soup.find('span', class_="qTHqo _1mEoj _2h9me DYJ1Y _2FQ5q _2GT-y"):
                break
            i += 1

        for elem in li:
            sal = elem.find('span', class_="_3mfro _2Wp8I _1qw9T f-test-text-company-item-salary PlM3e _2JVkc _2VHxz")
            res.append({'vacancy_name': elem.find('div', class_="_3mfro PlM3e _2JVkc _3LJqf").text,
                        'link': service_2 + elem.find('a').attrs['href'],
                        'salary': self._salary_range(sal.text) if not sal.text.startswith('По') else None,
                        'service': service_2})

        return res

    def _prepare_collection_name(self) -> str:

        # функция создает английское имя, которое по дефолту используется для коллекции
        # (актуально если key_words заданы на русском языке)

        params = {'key': 'trnsl.1.1.20200521T103802Z.e3e619c42b0613bc.c13a1d33a52c9b0886519c227b753fcf2da1d646',
                  'text': self.vacancy, 'lang': 'ru-en'}
        resp = requests.get('https://translate.yandex.net/api/v1.5/tr.json/detect', params=params)

        if json.loads(resp.text)['lang'] == 'ru':
            resp_2 = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate', params=params)
            result = json.loads(resp_2.text)['text'][0]
        else:
            result = self.vacancy

        return re.sub(r'\s+', r'_', result).lower()

    def insert_data_into_db(self) -> None:

        # метод добавляет все записи, полученные при парсинге в бд, и выводит на печать их количество
        # реализована обработка исключения в случае, если метод вызван, когда key_words не заданы

        try:
            self.db[self.collection_name].insert_many(self.vacancy_list)
            print('collection {} update: {} vacancies were inserted '.format(self.collection_name,
                                                                             len(self.vacancy_list)))
        except TypeError:
            print('{}: there are no data to insert'.format(__name__))

    def add_new_data_into_db(self) -> None:

        # метод добавляет только новые записи, полученные при парсинге в бд, и выводит на печать их количество
        # реализована обработка исключения в случае, если метод вызван, когда key_words не заданы

        try:
            i = 0
            for elem in self.vacancy_list:
                if not self.db[self.collection_name].find(
                        {'link': elem['link'], 'vacancy_name': elem['vacancy_name']}).count():
                    self.db[self.collection_name].insert_one(elem)
                    i += 1
            print('Collection {} update: {}/{} vacancies were inserted '.format(self.collection_name,
                                                                                i, len(self.vacancy_list)))
        except TypeError:
            print('{}: there are no data to add'.format(__name__))

    def vacancy_salary_gt(self, value: int, currency='руб'):

        # метод делает выгрузку вакансий из бд, с зп выше указанной
        try:
            res = self.db[self.collection_name].find({
                '$and': [
                    {
                        '$or': [
                            {'salary.min': {'$gt': value}},
                            {
                                '$and': [
                                    {'salary.min': None},
                                    {'salary.max': {'$gt': value}}
                                ]
                            }
                        ]
                    },
                    {'salary.currency': currency}
                ]
            })

            return res
        except TypeError:
            print('{}: collection undefined'.format(__name__))


