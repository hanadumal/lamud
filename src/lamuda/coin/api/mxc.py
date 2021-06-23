from lamuda.http.request import Http


class Mxc(object):
    base_path = 'https://www.mxc.com'
    
    @staticmethod
    def query_symbol():
        """

        :return:
        """
        base_path = Mxc.base_path
        symbol_path = f'{base_path}/open/api/v2/market/symbols'
        rp = Http.get(symbol_path, None)
    
    @staticmethod
    def get_ohlcv(symbol, timeframe='1d', limit=200):
        """ 获取ohlcv数据
        """
        symbol = '_'.join(symbol.split('/'))
        base_path = Mxc.base_path
        candle_path = f'{base_path}/open/api/v2/market/kline'
        params = {"symbol": symbol,
                  "interval": timeframe,
                  "limit": limit}
        rp = Http.get(candle_path, params)
        #           time  open  high  low   close  vol
        result = [ [i[0], float(i[1]), float(i[3]), float(i[4]), float(i[2]), float(i[5])] for i in rp['data']]
        return result
        
        
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
