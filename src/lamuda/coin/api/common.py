import re

from .binance import Binance
from .huobi import Huobi
from .mxc import Mxc

binance = Binance()
huobi = Huobi()
mxc = Mxc()

def get_ohlcv(symbol, timeframe='1d', limit=200):
    """获取ohlcvs数据
    1.优先从币安接口
    2.尝试火币接口
    3.尝试抹茶接口
    """
    ohlcvs = binance.get_ohlcv(symbol, timeframe, limit)
    if ohlcvs is None:
        ohlcvs = huobi.get_ohlcv(symbol, timeframe, limit)
    if ohlcvs is None:
        ohlcvs = mxc.get_ohlcv(symbol, timeframe, limit)
    return ohlcvs


def get_cur_price(symbol):
    """
     0     1     2.    3.    4.     5
    time  open  high  low   close  vol
    """
    cur_price = get_ohlcv(symbol)[-1][4]
    return cur_price


def format_symbol(s):
    """ 格式化交易对字符串, 输出格式为 BTC/USDT
    """
    buf = re.split(',|-|/|_', str.upper(s))
    if len(buf) == 1:
        symbol = f'{buf[0]}/USDT'
    if len(buf) == 2:
        symbol = f'{buf[0]}/{buf[1]}'
    return symbol