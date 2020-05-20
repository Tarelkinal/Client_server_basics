import requests
from bs4 import BeautifulSoup
import re
from pprint import pprint


def get_vacancy_list(vacancy, num_pages_to_parse=None):

    def _salary_range(string):
        # функция парсит информацию о зарплате на категории

        if string.startswith('от'):
            salary = {'min': ''.join(re.findall(r'от\s(\d+)\s(\d*)', string)[0]),
                      'max': None}
        elif string.startswith('до'):
            salary = {'min': None,
                      'max': ''.join(re.findall(r'до\s(\d+)\s(\d*)', string)[0])}
        elif re.search(r'[-—]', string):
            salary = {'min': ''.join(re.findall(r'(\d+)\s*(\d*)\s*[-—]', string)[0]),
                      'max': ''.join(re.findall(r'[-—]\s*(\d+)\s(\d*)', string)[0])}
        else:
            salary = {'min': ''.join(re.findall(r'(\d+)\s(\d*)', string)[0]),
                      'max': ''.join(re.findall(r'(\d+)\s(\d*)', string)[0])}
        salary['currency'] = re.findall(r'\s(\w+)\.*$', string)[0]
        return salary

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/81.0.4044.113 YaBrowser/20.4.1.225 Yowser/2.5 Safari/537.36'}

    service = 'https://hh.ru'
    service_2 = 'https://www.superjob.ru'

    li = []
    i = 0
    while i < num_pages_to_parse if num_pages_to_parse is not None else True:  # парсим заданное количество страниц или все, если не задано
        request = f'{service}/search/vacancy?area=1&text={vacancy}&page={i}'
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
            'salary': _salary_range(elem.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}).text) if elem.find('span', {
            'data-qa': "vacancy-serp__vacancy-compensation"}) is not None else None,
            'service': service} for elem in li]

    # все тоже самое для https://www.superjob.ru
    li = []
    i = 1
    while i < num_pages_to_parse + 1 if num_pages_to_parse is not None else True:
        request = f'{service_2}/vacancy/search/'
        params = {'keywords': vacancy, 'page': i}
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
        res.append({'vacancy_name': elem.find('div', class_="_3mfro CuJz5 PlM3e _2JVkc _3LJqf").text,
                      'link': service_2 + li[1].find('a').attrs['href'],
                      'salary': _salary_range(sal.text) if not sal.text.startswith('По') else None,
                      'service': service_2})
    return res


if __name__ == '__main__':
    with open('vacancy_list.json', 'w', encoding='utf8') as f:
        pprint(get_vacancy_list('Физик'), f)

