"""
Encapsul of requests
"""
import logging
from urllib import parse

import requests


class Http(object):
    logger = logging.getLogger(f'{__name__}.Http')

    @staticmethod
    def request(url, params, method="GET", user_agent='Mozilla 5.10'):
        """If return status not 200, return None, else return a dict.

        :param method:
        :param url:
        :param params:
        :param user_agent:
        :return:
        """
        headers = {
            "Accept-Charset": "UTF-8",
            "Content-type": "application/json",
            "User-agent": user_agent,
        }

        if method == 'GET':
            if params:
                payload = parse.urlencode(params)
            else:
                payload = {}
            response = requests.get(url, payload, headers=headers)
        elif method == 'POST':
            # todo: 实现post方法
            pass

        if response.status_code == 200:
            result_data = response.json()
            Http.logger.info(result_data)
            return result_data
        return None

    @staticmethod
    def get(url, params: dict = {}):
        return Http.request(url, params)

    @staticmethod
    def post(url, params: dict = {}):
        return Http.request(url, params, method="POST")

