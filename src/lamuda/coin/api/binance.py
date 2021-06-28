import logging
import time

import ccxt
import numpy as np
import pandas as pd

from .base import BaseExchange
from ...date.common_date import CommonDate


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
        
    def get_ohlcv(self, symbol, timeframe='1d', limit=200):
        if symbol in self.api.markets:
            time.sleep(self.api.rateLimit/1000)
            self.logger.info(f"get symbol ohlcv: {symbol}")
            # fetchOHLCV (symbol, timeframe = '1m', since = undefined, limit = undefined, params = {})
            # result array is order by microsec ascending
            # [[ms, open, high, low, close, vol],[]]
            return self.api.fetch_ohlcv(symbol, timeframe, limit=limit)
        return None

    def get_ohlcv_df(self, symbol, timeframe='1d', limit=200):
        klines = self.get_ohlcv(symbol, timeframe, limit)
        klines_nd = np.array(klines)
        df = pd.DataFrame({'id':    klines_nd[0],
                           'open':  klines_nd[1],
                           'high':  klines_nd[2],
                           'low':   klines_nd[3],
                           'close': klines_nd[4],
                           'vol':   klines_nd[5]
                           })
        df['t'] = df['id'].apply(CommonDate.mts_iso())
        return df