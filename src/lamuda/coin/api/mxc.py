from lamuda.http import Http


class Mxc(object):
    @staticmethod
    def query_symbol():
        """

        :return:
        """
        base_path = 'https://www.mxc.com'
        symbol_path = f'{base_path}/open/api/v2/market/symbols'
        print(symbol_path)
        rp = Http.get(symbol_path, None)
        print(rp)

    @staticmethod
    def query_kline(symbol, ktype="1m", limit=240):
        """
        time, open, close, high, low, vol, amout
        [1614602100, '3.216', '3.213', '3.217', '3.213', '74.63', '239.98863']
        :param symbol: symbol to query
        :param ktype:  kline type： 1m 1d
        :param limit:  number of candles to query
        :return:
        """
        base_path = 'https://www.mxc.com'
        candle_path = f'{base_path}/open/api/v2/market/kline'
        params = {"symbol": symbol,
                  "interval": ktype,
                  "limit": limit}
        rp = Http.get(candle_path, params)
        print(rp['data'][-1])
        return rp['data'][-1]

    @staticmethod
    def query_kline_newest():
        """Return the newest minute kline."""
        return Mxc.query_kline("1m", 1)
