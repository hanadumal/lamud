from enum import Enum
import logging

class FirstResult(Enum):
    INCREASE_DOWN_HOR = 1 # MACD线斜率为正，MACD
    INCREASE_UP_HOR = 2
    DECREASE_UP_HOR = 3
    DECREASE_DOWN_HOR = 4

class Action(Enum):
    BUY = 1
    SELL = 2


class ThreeFilter(object):
    """ 三重滤网交易系统
        为了过滤掉趋势跟随指标和震荡指标的缺陷，同时保留它们的优势。
        
    """
    def __init__(self):
        pass

    def first_filter(self, macd):
        """ 以1小时为中期时间周期，4小时为长期时间周期。重点是先分析长周期的趋势，然后在中周期寻找机会，但是要遵循长周期的趋势方向。
        第一步，用长时间周期判断趋势是熊还是牛。
        第二步，回到中期时间周期，在决策，在什么位置买，在什么位置设置止损。
        
        具体操作：判断MACD柱，最近两根的变化趋势。如果相邻斜率为正，则允许买入/观望。如果相邻的斜率为负，则允许卖出/观望。
        过滤逻辑：帮助过滤掉买入、卖出、观望中的一个选项。
        :param macd: dict
        :return: 1 2 代表可买入，3 4代表可卖出，但是1比2好，3比4好
        """
        vs = list(macd.values())
        change = vs[-1] - vs[-2]
        if change > 0 and vs[-1] < 0:
            # 斜率为正，最近的MACD柱在0线下，这是最好的买入场景
            result = FirstResult.INCREASE_DOWN_HOR
        elif change > 0 and vs[-1] > 0:
            # 斜率为正，最近的MACD柱在0线上，这是次之的买入场景
            result = FirstResult.INCREASE_UP_HOR
        elif change < 0 and vs[-1] > 0:
            # 斜率为负，最近MACD在0线上，这是最好的卖出场景
            result = FirstResult.DECREASE_UP_HOR
        elif change < 0 and vs[-1] < 0:
            # 斜率为负，最近MACD柱在0线下，这是次好的卖出场景
            result = FirstResult.DECREASE_DOWN_HOR
        logging.info(f"第一层过滤结果：{result}")
        return result

    def second_filter(self, ohlcvs):
        """ 用的是震荡指标，找到与长周期方向一致的 中周期的信号。传入参数均为中周期的参数
        长周期上升，利用中周期的回调来买入；长周期下降，利用中周期的反弹来卖出。
        计算窗口为2的，强力指标EMA，强力指标为负数允许买入；强力指标为正数允许卖出。
        
        :param ohlcvs: [[time open high low close vol], [time open high low close vol]]
        :return: 最新周期的强力指标得分
        """
        # 初始化
        last = 0
        ema = 0
        size = 2
        smoothing = 2
        for i in ohlcvs:
            #（本周期的收盘 - 开盘 ） * 成交量
            value = (i[4] - i[1]) * i[5]
            ema = (smoothing/(1+size) * value) + (1 - smoothing/(1+size)) * last
            last = ema
        logging.info(f"第二层过滤强力指标得分: {ema}")
        return ema
            
        
        

    def third_filter(self, close_prices, ema1s, action, size=14):
        """ 第三层控制买入价格，或者卖出价格
        # Todo: 是否换成更短的时间周期，1小时的时间窗口
        :param close_prices: 收盘价，[(时间，收盘价)]
        :param ema1s: 短期的EMA      {时间：收盘价, 时间：收盘价}
        :param action: 动作，根据不同的动作，计算推荐买入/卖出的价格
        :return: 在最近的size窗口内，收盘价跌破快速EMA的均价
        """
        if action == 'BUY':
            fall_over_count = 0
            fall_over_totoal = 0
            for i in range(1, size+1):
                diff = close_prices[-i][1] - list(ema1s.values())[-i]
                if diff < 0:
                    fall_over_count += 1
                    # 这个值为负数，不取abs, 下面直接跟最新价格相加
                    fall_over_totoal += diff
            newest_price = close_prices[-1][1]
            delta = 0
            # 计算平均收盘价跌破快速EMA的均值
            if fall_over_count != 0:
                delta = fall_over_totoal/fall_over_count
                price = newest_price - delta
            else:
                # 若一直未跌破均价, 则在前一日收盘价格基础上增加前一的成本
                # Todo: 这里应该改为前一日高点的位置上增加相应的delta
                price = close_prices[-2][1] * 1.01
            logging.info(f"第三层过滤: 最新价格 {newest_price} 平均跌破:{delta} 推荐的价格:{price}")
        else:
            up_count = 0
            up_total = 0
            for i in range(1, size+1):
                # 计算收盘价涨破短期EMA的差值
                diff = close_prices[-i][1] - list(ema1s.values())[-i]
                if diff > 0:
                    up_count += 1
                    # 这个值为负数，不取abs, 下面直接跟最新价格相加
                    up_total += diff
            newest_price = close_prices[-1][1]
            delta = 0
            if  up_count != 0:
                delta = up_total/up_count
                price = newest_price + delta
            else:
                # 若一直未涨破短期EMA(也就是说在一路下跌）, 则在前一日收盘价格基础上减去一定的成本
                price = close_prices[-2][1] * 0.99
            logging.info(f"第三层过滤: 最新价格 {newest_price} 平均涨破:{delta} 推荐的价格:{price}")
            
        return price


    def run(self, long_macd, medium_close, medium_ema1, medium_ohlcvs):
        """ 
        :param long_macd: dict
        :param medium_close:
        :param medium_ema1:
        :param medium_ohlcvs:
        :return:
        """
        first_flag = self.first_filter(long_macd)
        second_flag = self.second_filter(medium_ohlcvs)
        if first_flag in (FirstResult.INCREASE_UP_HOR, FirstResult.INCREASE_DOWN_HOR):
            if second_flag <= 0:
                action = Action.BUY
                buy_price = self.third_filter(medium_close, medium_ema1, 'BUY')
                return action, buy_price, first_flag
        elif first_flag in (FirstResult.DECREASE_UP_HOR, FirstResult.DECREASE_DOWN_HOR):
            if second_flag >= 0:
                action = Action.SELL
                sell_price = self.third_filter(medium_close, medium_ema1, 'SELL')
                return action, sell_price, first_flag
        else:
            logging.info(f"无推荐操作")
            return None
            
    
