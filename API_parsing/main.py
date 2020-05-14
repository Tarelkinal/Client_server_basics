import requests
import json
from pprint import pprint

# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.


head = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def git_repos_list(username):

    repos = requests.get(f'https://api.github.com/users/{username}/repos')

    with open(f'{username}_repos_list.json', 'w', encoding='utf8') as f:
        pprint(json.loads(repos.text), f)


# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
# пройдя авторизацию. Ответ сервера записать в файл.

API_key = '0fc48a977fcdcb8b8968e340'


def get_currency_exchange_rate(currency, API_key):
    rate = requests.get(f'https://prime.exchangerate-api.com/v5/{API_key}/latest/{currency}')

    with open(f'{currency}_exchange_rate.json', 'w', encoding='utf8') as f:
        pprint(json.loads(rate.text), f)


if __name__ == '__main__':
    git_repos_list('Tarelkinal')
    get_currency_exchange_rate('RUB', API_key)