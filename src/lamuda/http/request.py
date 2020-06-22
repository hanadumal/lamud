"""
Encapsul of requests
"""
import logging
from urllib import parse

import requests


class Request(object):
    logger = logging.getLogger(f'{__name__}.Request')

    @staticmethod
    def request_url(url, params, user_agent='Mozilla 5.10'):
        """If return status not 200, return None, else return a dict.

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
        post_data = parse.urlencode(params)
        raw_data = requests.get(url, post_data, headers=headers)
        if raw_data.status_code == 200:
            result_data = raw_data.json()
            Request.logger.info(result_data)
            return result_data
        return None
