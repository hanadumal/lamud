import logging
import time

import ccxt

from base import BaseExchange

class Binance(BaseExchange):
    """
    """
    def __init__(self):
        super().__init__()
        self.name = 'Binance'
        self.logger = logging.getLogger(f'{__name__}.{self.name}')
        
        self.api = ccxt.binance()
        
        self.api.enableRateLimit = True
        self.api.rateLimit = 200
        dict_market = self.api.load_markets()
    
    def quote_price_exchange(self, dict_market):
        pass
        
    def get_ohlcv(self, symbol, timeframe='1d'):
        if symbol in self.api.markets:
            time.sleep(self.api.rateLimit/1000)
            self.logger.warning(f"get symbol ohlcv: {symbol}")
            # fetchOHLCV (symbol, timeframe = '1m', since = undefined, limit = undefined, params = {})
            # result array is order by microsec ascending
            # [[ms, open, high, low, close, vol],[]]
            return self.api.fetch_ohlcv(symbol, timeframe, limit=200)
        return None