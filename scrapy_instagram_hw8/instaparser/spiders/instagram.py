# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from scrapy_instagram_hw8.instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    insta_login = 'g-ydvi-n@mail.ru'
    insta_pass = '#PWD_INSTAGRAM_BROWSER:10:1592299235:ARNQAKEreLuKjWW6tKixSNnZgS8+gy1L6etvuIpvRG7qpRdBHQg4Gf2HAZ2x1MbZCmdB255GQGSI2B7UKrUUV/pXL+TL+mJ6Zb+jOsbuZRHh49VjI392G3UAb55DyVDt8SiGFrT6PpBu3vAsd+Pu5Nzt8A=='
    inst_login_link = 'https://instagram.com/accounts/login/ajax/'
    parser_users = ['gitarist3099', 'gitar123', 'dfssaggfa']
    hash_followers = 'c76146de99bb02f6415203be841dd25a'
    hash_following = 'd04b0a864b4b54837c0d870b0e77e076'
    graphql_url = 'https://www.instagram.com/graphql/query/?'

    # 'kDG8MW9CUL6jc5HR9zyhXJVkKt26WvVZ'
    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.parse_user,
            formdata={'username': self.insta_login,
                      'enc_password': self.insta_pass},
            headers={'X-CSRFToken': csrf_token}
        )

        pass

    @staticmethod
    def fetch_csrf_token(text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')


    def parse_user(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for user in self.parser_users:
                yield response.follow(
                    f'{self.start_urls[0]}{user}/',
                    callback=self.user_data_parse,
                    cb_kwargs={'user': user}
                )

    def user_data_parse(self, response: HtmlResponse, user):
        user_id = re.findall(r'"profilePage_(\d+)"', response.text)[0]
        variables = {'id': user_id, 'include_reel': True, 'fetch_mutual': True, 'first': 24}
        url_followers = f'{self.graphql_url}query_hash={self.hash_followers}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.followers_parse,
            cb_kwargs={'variables': deepcopy(variables),
                       'user_name': user,
                       'user_id': user_id}
        )

        url_following = f'{self.graphql_url}query_hash={self.hash_following}&{urlencode(variables)}'
        yield response.follow(
            url_following,
            callback=self.following_parse,
            cb_kwargs={'variables': deepcopy(variables),
                       'user_name': user,
                       'user_id': user_id}
        )

    def followers_parse(self, response, variables, user_name, user_id):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_followed_by').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_followers = f'{self.graphql_url}query_hash={self.hash_followers}&{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'variables': deepcopy(variables),
                           'user_name': user_name,
                           'user_id': user_id}
            )
        followers = j_body.get('data').get('user').get('edge_followed_by').get('edges')
        for follower in followers:
            item = InstaparserItem(
                origin_user_name=user_name,
                origin_user_id=user_id,
                user_name=follower['node']['username'],
                photo=follower['node']['profile_pic_url'],
                status='follower'
            )

            yield item

    def following_parse(self, response, variables, user_name, user_id):
        j_body = json.loads(response.text)
        page_info = j_body.get('data').get('user').get('edge_follow').get('page_info')
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url_followers = f'{self.graphql_url}query_hash={self.hash_followers}&{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'variables': deepcopy(variables),
                           'user_name': user_name,
                           'user_id': user_id}
            )
        followers = j_body.get('data').get('user').get('edge_follow').get('edges')
        for follower in followers:
            item = InstaparserItem(
                origin_user_name=user_name,
                origin_user_id=user_id,
                user_name=follower['node']['username'],
                photo=follower['node']['profile_pic_url'],
                status='following'
            )

            yield item
