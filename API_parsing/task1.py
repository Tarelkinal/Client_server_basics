import requests
import json
from pprint import pprint

# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.


def git_repos_list(username):

    repos = requests.get(f'https://api.github.com/users/{username}/repos')

    with open(f'{username}_repos_list.json', 'w', encoding='utf8') as f:
        pprint(json.loads(repos.text), f)


if __name__ == '__main__':
    git_repos_list('Tarelkinal')

