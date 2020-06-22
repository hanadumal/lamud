from lamuda.http.request import Request


class TestRequest(object):
    def test_request_url(self):
        url = 'https://api.hbdm.com/market/history/kline'
        params = {'period': '1min', 'size': 40, 'symbol': 'BTC_CW'}
        Request.request_url(url, params)
