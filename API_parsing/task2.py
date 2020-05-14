import requests
import json
from pprint import pprint

# 2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа). Выполнить запросы к нему,
# пройдя авторизацию. Ответ сервера записать в файл.

API_key = '0fc48a977fcdcb8b8968e340'


def get_currency_exchange_rate(currency, API_key):
    rate = requests.get(f'https://prime.exchangerate-api.com/v5/{API_key}/latest/{currency}')

    with open(f'{currency}_exchange_rate.json', 'w', encoding='utf8') as f:
        pprint(json.loads(rate.text), f)


if __name__ == '__main__':
    get_currency_exchange_rate('RUB', API_key)
