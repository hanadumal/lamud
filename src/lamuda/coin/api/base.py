from abc import ABCMeta, abstractmethod
import pandas as pd
import logging

pd.set_option('precision', 10)
# 显示所有列
pd.set_option('display.max_columns', 500)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置value的显示长度为100，默认为50
pd.set_option('max_colwidth', 100)
# 设置展示宽度最大为1000
pd.set_option('display.width', 1000)


class BaseExchange(metaclass=ABCMeta):
    depth_level = [0.1, 0.5, 1]
    amount_level = [10, 100, 1000, 10000, 20000, 50000, 100000]
    k15_symbol_list = ['IOTA/USDT', 'BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'EOS/USDT',
                       'LTC/USDT', 'BCH/USDT', 'ETC/USDT', 'XLM/USDT', 'ADA/USDT',
                       'XMR/USDT', 'DASH/USDT', 'ZEC/USDT', 'OMG/USDT', 'BSV/USDT']
    # k15_symbol_list = ['BTC/USDT']

    @abstractmethod
    def __init__(self):
        self.api = None
        self.name = None
        self.logger = logging.getLogger('{module}.{c}'.format(module=__name__, c='Base'))
        self.symbol_list = None
        self.symbols = None
        self.price_dict = None

    @abstractmethod
    def quote_price_exchange(self, dict_market):
        pass

    def fetch_ticker_info(self, symbol):
        """
        general ticker data get method
        :param symbol:
        :return:
        """
        try:
            ticker_info = self.api.fetchTicker(symbol)
            return ticker_info
        except Exception as e:
            self.logger.warning(f'fetch ticker error {e}')
            return None

    def fetch_order_book(self, symbol):
        """ Fetch symbol's order_book

                :param symbol:
                :return: order_book dict: {symbol: symbol_name, ask: DataFrame([price, vol]) , bid:DataFrame([price, vol]) }
                """
        res = {}
        try:
            order_book = self.api.fetch_l2_order_book(symbol)
            # 取得quote兑换usdt的价格
            quote_price_usdt = self.price_dict[symbol.split('/')[1]]
            # bid: 买，降序排列
            res['bid'] = pd.DataFrame(order_book['bids'], columns=['price', 'vol']).sort_values('price',
                                                                                                ascending=False)
            # ask: 卖，增序排列
            res['ask'] = pd.DataFrame(order_book['asks'], columns=['price', 'vol']).sort_values('price',
                                                                                                ascending=True)
            res['symbol'] = symbol
            res['quote_price_usdt'] = quote_price_usdt
            return res
        # Todo: bare Exception
        except Exception as e:
            self.logger.info(f'{self.name} has no symbol {symbol}')

    def fetch_vol_data(self):
        """Fetch symbol 24h vol data

        :return: {symbol1: vol1, symbol2: vol2, ...}
        """
        res = {}
        for symbol in self.symbols:
            vol_data = self.fetch_ticker_info(symbol)
            quote = symbol.split('/')[1]
            res[symbol] = vol_data.get('quoteVolume', 0.0) * self.price_dict.get(quote)
            self.logger.info(f'vol one symbol -- {symbol}:{vol_data["quoteVolume"] * self.price_dict.get(quote)}')
        self.logger.info(f'vol_info:{res}')
        return res

    def cal_slippage_in_amount(self, orderbook, amount):
        """
        process orderbook and calculate all amount level slippage
        :param orderbook: orderbook data
        :param amount: single amount
        :return: slippage data and slippage_depth data medium
        # """
        mid_price = (orderbook['bid']['price'].iloc[0] + orderbook['ask']['price'].iloc[0]) / 2
        depth, slippage = pd.DataFrame(
             [self.cal_slippage_in_amount_one_side(orderbook, side, amount, mid_price) for side in ('ask', 'bid')]
        ).mean()
        return depth, slippage

    def cal_slippage_in_amount_one_side(self, orderbook, side, amount, mid_price):
        """
        calculate single side slippage data
        :param orderbook: orderbook data
        :param side: bid ask
        :param amount: single amount
        :param mid_price: mid price (ask1+bid1)/2
        :return: slippage data and slippage_depth data
        """
        # spread过大，传入的深度档位对应amount为0，返回0， 0
        if amount <= 0:
            return 0, 0
        order_book_one_side = orderbook[side]
        quote_price_usdt = orderbook['quote_price_usdt']
        orderbook_one_side_length = len(order_book_one_side)
        selected_data = order_book_one_side[order_book_one_side['cum_amount'] < amount]
        selected_data_length = len(selected_data)

        if selected_data_length == orderbook_one_side_length:
            last_row_price = order_book_one_side.iloc[-1]['price']
            depth = abs(last_row_price - mid_price) / mid_price
            total_vol = order_book_one_side['vol'].sum()
            avg_price = order_book_one_side.iloc[-1]['cum_amount'] / (total_vol * quote_price_usdt)
            slippage = abs(avg_price / mid_price - 1)
            self.logger.debug(f'''side: {side}, usdt: {amount}, avg_price :{avg_price}, mid_price :{mid_price}, 
                total_vol(base): {total_vol}, slippage: {slippage}, depth: {depth}''')
            return depth, slippage
        else:

            # 1. 如果第一档的cum_amount  > 需要的amount; 那么最后一档（也就是第一档)填充的amount = amount - 0
            # 2. 否则，使用<需要的amount> - <selected最后一档的累计cum_amount> = <最后一档的下一个档位需要填充的amount>
            # 3. 由selected最后一档的下一档的vol = (剩余amount/该档的price)
            last_row_amount = amount - (0 if selected_data_length == 0 else selected_data['cum_amount'].iloc[-1])
            last_price = order_book_one_side['price'].iloc[selected_data_length]
            # last_row_vol : base币种的量
            # amount_usdt/quote_price_usdt = quote_amount
            # quote_amount / last_price = base_amount = vol
            last_row_vol = last_row_amount / (last_price * quote_price_usdt)
            total_vol = selected_data['vol'].sum() + last_row_vol
            avg_price = amount / (total_vol * quote_price_usdt)
            slippage = abs(avg_price / mid_price - 1)
            depth = abs(last_price - mid_price) / mid_price
            self.logger.debug(f'''side: {side}, usdt: {amount}, avg_price :{avg_price}, mid_price :{mid_price}, 
                total_vol(base): {total_vol}, slippage: {slippage}, depth: {depth}''')
            return depth, slippage

    def fetch_slippage_data(self):
        """
        calculate slippage and depth_slippage
        :return:
        """
        res = {}
        for symbol in self.symbols:
            order_book = self.fetch_order_book(symbol)

            # 如果某交易所，没有该symbol
            if order_book is None:
                continue
            tmp = {}

            # 获取不同档位对应的深度USDT数值
            depth_amount_dict = self.calc_depth_level_amount(order_book)
            if depth_amount_dict is None:
                continue
            # self.logger.info(depth_amount_dict)

            mid_price = (order_book['bid']['price'].iloc[0] + order_book['ask']['price'].iloc[0]) / 2
            # {0.1: {'bid': 262476.45460025, 'ask': 264945.02336025}}
            for key, value in depth_amount_dict.items():
                amount_a = value['ask']
                d_a, s_a = self.cal_slippage_in_amount_one_side(order_book, 'bid', amount_a, mid_price)
                amount_b = value['bid']
                d_b, s_b = self.cal_slippage_in_amount_one_side(order_book, 'ask', amount_b, mid_price)

                amount = (amount_a + amount_b) / 2
                slippage = (s_a + s_b) / 2
                tmp.update({f'{key}_depth_amount': amount, f'{key}_depth_slippage': slippage})
            # 计算不同数值USDT: 10, 100, 1k, 10k ... 对应的滑点
            for amount in BaseExchange.amount_level:
                depth, slippage = self.cal_slippage_in_amount(order_book, amount)
                tmp.update({f'{amount}_amount_depth': depth, f'{amount}_amount_slippage': slippage})

            res.update({order_book['symbol']: tmp})
            # self.logger.info(res)
            self.logger.info(f'symbol {symbol} done!!!')
        self.logger.info(pd.DataFrame(res))
        return res

    def calc_depth_level_amount(self, order_book):
        """根据深度档位计算深度数值, 如: 0.1% -> 8000u

        :orderbook: pd.DataFrame()
        :return:
        """
        ask_df = order_book['ask']
        bid_df = order_book['bid']
        quote_price_usdt = order_book['quote_price_usdt']

        ask_df['amount'] = ask_df['price'] * ask_df['vol'] * quote_price_usdt
        ask_df['cum_amount'] = ask_df['amount'].cumsum()

        bid_df['amount'] = bid_df['price'] * bid_df['vol'] * quote_price_usdt
        bid_df['cum_amount'] = bid_df['amount'].cumsum()

        # self.logger.info(f'ask_df: {ask_df} \n bid_df: {bid_df}')
        if len(ask_df) > 0 and len(bid_df) > 0:
            mid_price = (ask_df.iloc[0]['price'] + bid_df.iloc[0]['price'])/2
            # self.logger.info(f'ask:{ask_df.iloc[0]["price"]} mid_price: {mid_price}')
            level_dict = {}
            for level in self.depth_level:
                level_price_bid = mid_price * (1 - level / 100)
                level_price_ask = mid_price * (1 + level / 100)
                # 价差过大， 0.1%深度取不到，特殊处理深度为0，滑点为0
                bid_sum_depth = 0 if bid_df[bid_df['price'] > level_price_bid].empty else bid_df[bid_df['price'] > level_price_bid].iloc[-1]['cum_amount']
                ask_sum_depth = 0 if ask_df[ask_df['price'] < level_price_ask].empty else ask_df[ask_df['price'] < level_price_ask].iloc[-1]['cum_amount']
                level_dict[level] = {'bid': bid_sum_depth, 'ask': ask_sum_depth}
                # self.logger.info(f'level_dict: {level_dict}')
            return level_dict
        else:
            self.logger.warning(f'{order_book["symbol"]} order book ask or bid is null!')
            return None

