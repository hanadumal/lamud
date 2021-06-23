import logging
import time
import ccxt
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt

from .conf    import ma1_size, ma2_size, dea_size
from .conf    import point_limit


pd.set_option('precision', 10)


def calc_sma(candles, wsize):
    """
    @param candles: list, element (time_str, value)
    @param msize:   int,  window size
    @return result: list((time_str1, sma1), (time_str2, sma2),...)
    """
    if len(candles) < wsize:
        logging.warning(f'len(candels) less than {wsize}, return None')
        return None

    result = []

    for i in range(0, len(candles)):
        # wsize=4
        # 第一个非None数值下标范围: 0:4 
        # 第二个非None数值下标范围: 1:5 
        # 第二个非None数值下标范围: 2:6
        # 最前面的wsize-1个sma为None
        # 边界情况：sma[wsize-1] = 前wsize个数的平均值
        if i < wsize-1:
            item=(candles[i][0], None)
        else:
            # l[:i] 不包含最后一位
            item = (candles[i][0]) , round(sum([c[1] for c in candles[i+1-wsize:i+1]])/wsize, 6)
        result.append(item)
    return result
    

def calc_ema(init, values, wsize, smoothing=2):
    """
    @param init:   float
    @param values: list
    @param wsize:  int, window size
    @smoothing: factor that decide the weight of recent value
    @return ema_result: dict {time_str1: ema1, time_str2: ema2, ...}, length will be same with values
    """
    # exponential moving average 
    # EMA(Today)=(ValueToday ∗ Smoothing/(1+WindowSize)) + EMAYesterday∗ (1− Smoothing/(1+WindowSize))
    # EMA = Closing price x multiplier + EMA (previous day) x (1-multiplier)
    # The result length will have len(values) - wsize
    # ex. 30 days data for values array, compute 20day-ema, there will be only 10 result
    ema_last = init
    ema_result = {}
    logging.info(f'最初的EMA ema_last:{ema_last}')
    for i in range(0, len(values)):
        k = values[i][0]
        v = values[i][1]
        # 前面wsize个EMA,设置为None
        if i < wsize:
            ema_result[k] = None
        logging.debug(f"{k} 最新价格:{v} 上一个ema:{ema_last}")
        ema = round( v * smoothing/(1+wsize) + ema_last * (1-smoothing/(1+wsize)), 6)
        ema_result[k] = ema
        # 更新上一次EMA
        ema_last = ema
    return ema_result

def calc_macd(emas1, emas2):
    """
    @emas1: dict short time ema
    @emas2: dict long time ema
    @return dif: list
    @return dea: dict
    """
    dif_res=[]
    dea_res={}
    macd={}
    # 先计算DIF
    for item in emas2.keys():
        diff = emas1[item] - emas2[item]
        dif_res.append((item, diff))
        logging.debug(f"{item} ema1:{emas1[item]} ema2:{emas2[item]} diff:{diff}")
    init = sum([d[1] for d in dif_res[:dea_size]])/dea_size
    dea_res = calc_ema(init, dif_res, dea_size)
    for i in range(0, len(dif_res)):
        key = dif_res[i][0]
        if key in dea_res:
            m = dif_res[i][1] - dea_res[key]
        else:
            m = None
        macd[key] = m
    return dif_res, dea_res, macd


def draw_histogram(s, title, file_path, limit=point_limit):
    fig, ax = plt.subplots()
    ax.bar(list(s.keys())[limit:], list(s.values())[limit:], label='MACD')
    
    ax.set_xlabel('Datetime')
    ax.set_ylabel('Value')
    ax.set_title(title)
    ax.legend()
    fig.set_size_inches(18, 10)
    plt.xticks(rotation=270)
    plt.savefig(file_path)
    # plt.show()

def draw_line(s1, s2, sv, title, file_path, limit=point_limit):
    """
    @param s1
    @param s2
    """
    fig, ax = plt.subplots()
    fig.set_size_inches(18, 10)
    ax.plot(list(s1.keys())[limit:], list(s1.values())[limit:], marker='o', label=f'ema {ma1_size}', color='white')
    ax.plot(list(s2.keys())[limit:], list(s2.values())[limit:], marker='o', label=f'ema {ma2_size}', color='yellow')
    ks = [v[0] for v in sv]
    ps = [v[1] for v in sv]
    ax.plot(ks[limit:], ps[limit:], marker='o', label='price', color='green', linewidth=3)
    ax.set_facecolor("black")
    ax.set_title(title)
    ax.legend()
    plt.grid(linestyle='-.')
    plt.xticks(rotation=270)
    plt.savefig(file_path)
    # plt.show()
    
def foo(ohlcvs, symbol, path):
    if ohlcvs is None: 
        return None
    closes = [(datetime.fromtimestamp(i[0]/1000).strftime('%m%d %H'), i[4]) for i in ohlcvs]

    smas1 = calc_sma(closes, ma1_size)
    smas2 = calc_sma(closes, ma2_size)

    emas1 = calc_ema(smas1[ma1_size-1][1], closes, ma1_size)
    emas2 = calc_ema(smas2[ma2_size-1][1], closes, ma2_size)

    dif, dea, macd = calc_macd(emas1, emas2)
    
    kline_path = path + 'kline.jpg'
    draw_line(emas1, emas2, closes, f'{symbol} EMA', kline_path)
    
    hist_path = path + 'macd_histo.jpg'
    draw_histogram(macd, f'{symbol} MACD', hist_path)
    return dif, dea, macd
