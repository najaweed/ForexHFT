import redis
import numpy as np
db_redis = redis.Redis()

class RedisMarketLive:
    def __init__(self,
                 symbols:list,
                 num_ticks:int=20,
                 ):
        self.symbols = symbols
        self.num_ticks = num_ticks
        self.currencies = self._get_currencies()

    def _get_currencies(self):
        currencies = []
        for symbol in self.symbols:
            cur_1, cur_2 = symbol[:3], symbol[3:]
            if cur_1 not in currencies:
                currencies.append(cur_1)
            if cur_2 not in currencies:
                currencies.append(cur_2)
        return currencies

    def get_index_rates(self,):
        symbols_ticks = self.get_live_ticks()
        zero_like_raw = np.zeros_like(symbols_ticks[self.symbols[0]]['ask'])
        index_rates = {cur: {'price':zero_like_raw.copy(),'volume':zero_like_raw.copy()} for cur in self.currencies}

        for symbol, tick in symbols_ticks.items():
            cur_1, cur_2 = symbol[:3], symbol[3:]
            index_rates[cur_1]['price'] += np.log(tick['bid'])
            index_rates[cur_2]['price'] -= np.log(tick['ask'])

            index_rates[cur_1]['volume'] += tick['bid_size']
            index_rates[cur_2]['volume'] += tick['ask_size']
        return index_rates

    def get_live_ticks(self):
        symbols_ticks = {}
        for sym in self.symbols:
            raw = db_redis.lrange(sym, 0, self.num_ticks)
            ticks = {'ask': [], 'ask_size': [], 'bid': [], 'bid_size': []}
            for r in raw:
                dr = r.decode("utf-8")[1:-1]
                res = [float(value) for value in dr.split(', ')]
                ticks['ask'].append(res[0])
                ticks['ask_size'].append(res[1])
                ticks['bid'].append(res[2])
                ticks['bid_size'].append(res[3])
            for ty,tick in ticks.items():
                ticks[ty] = np.asarray(tick)
            symbols_ticks[sym] = ticks

        return symbols_ticks

#symbols = ['EURUSD', 'EURGBP', 'GBPUSD']

# r_live_market = RedisMarketLive(symbols)
# print(r_live_market.get_live_ticks())
# import matplotlib.pyplot as plt
# syms_ticks = r_live_market.get_live_ticks(2000)#r_live_market.get_index_rates(num_ticks=200)
# plt.figure('EURUSD')
# plt.plot(np.diff(syms_ticks['EURUSD']['ask']),'.--',c='r')
# plt.plot(np.diff(syms_ticks['EURUSD']['bid']),'.--',c='b')
#
# plt.figure('GBPUSD')
# plt.plot(np.diff(syms_ticks['GBPUSD']['ask']),'.--',c='r')
# plt.plot(np.diff(syms_ticks['GBPUSD']['bid']),'.--',c='b')
#
# plt.figure('EURGBP')
# plt.plot(np.diff(syms_ticks['EURGBP']['ask']),'.--',c='r')
# plt.plot(np.diff(syms_ticks['EURGBP']['bid']),'.--',c='b')
#
# plt.figure('EURUSDX')
# plt.plot(syms_ticks['EURUSD']['ask'],'.--',c='r')
# plt.plot(syms_ticks['EURUSD']['bid'],'.--',c='b')
#
# plt.figure('GBPUSDX')
# plt.plot(syms_ticks['GBPUSD']['ask'],'.--',c='r')
# plt.plot(syms_ticks['GBPUSD']['bid'],'.--',c='b')
#
# plt.figure('EURGBPX')
# plt.plot(syms_ticks['EURGBP']['ask'],'.--',c='r')
# plt.plot(syms_ticks['EURGBP']['bid'],'.--',c='b')
#
# plt.show()