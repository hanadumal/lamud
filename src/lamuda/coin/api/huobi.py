import logging
import time

import ccxt

from .base import BaseExchange

class Huobi(BaseExchange):
    """
    """
    def __init__(self):
        super().__init__()
        self.name = 'Huobi'
        self.logger = logging.getLogger(f'{__name__}.{self.name}')
        
        # 初始化交易所API实例
        self.api = ccxt.huobipro()
        self.api.enableRateLimit = True
        self.api.rateLimit = 200
        dict_market = self.api.load_markets()
    
    def quote_price_exchange(self, dict_market):
        pass
        
    def get_ohlcv(self, symbol, timeframe='1d', limit=2000):
        if symbol in self.api.markets:
            time.sleep(self.api.rateLimit/1000)
            self.logger.info(f"get symbol ohlcv: {symbol}")
            # fetchOHLCV (symbol, timeframe = '1m', since = undefined, limit = undefined, params = {})
            # result array is order by microsec ascending
            # [[ms, open, high, low, close, vol],[]]
            return self.api.fetch_ohlcv(symbol, timeframe, limit=limit)
        return None