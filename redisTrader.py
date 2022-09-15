from Signal.SignalRandom import SignalRandom
from Signal.SignalSpike import SpikeTrader
from Signal.SignalTriple import SignalTriple

from redisLiveMarket import RedisMarketLive

import time
from ManageOrder import ManageOrders
import MetaTrader5 as mt5

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


class Trader:
    def __init__(self,
                 symbols: list,
                 num_ticks: int = 100
                 # strategy_signal,
                 # config:dict,
                 ):
        self.symbols = symbols
        self.live_market = RedisMarketLive(self.symbols, num_ticks=num_ticks)
        self.manage_orders = ManageOrders(self.symbols)

    def _get_opened_requests(self) -> dict:
        symbols_requests = {}
        for symbol in self.symbols:
            positions = mt5.positions_get(symbol=symbol)
            if len(positions) > 0:
                if positions[0]._asdict()['type'] == 1:
                    symbols_requests[symbol] = 'SELL'
                elif positions[0]._asdict()['type'] == 0:
                    symbols_requests[symbol] = 'BUY'
            else:
                symbols_requests[symbol] = 'CLOSE'
        return symbols_requests

    def live_trader(self):
        symbols_ticks = self.live_market.get_live_ticks()
        indexes_ticks = self.live_market.get_index_rates()

        # print(symbols_ticks,indexes_ticks)
        # #print(live_order_books)
        new_signals = SignalTriple(symbols_ticks=symbols_ticks,
                                   indexes_ticks=indexes_ticks).signal()
        print(new_signals)
        last_position_state = self._get_opened_requests()
        print(last_position_state)
        self.manage_orders.manage_orders(last_position_state, new_signals)


symbols = ['EURUSD', 'EURGBP', 'GBPUSD']#

trader = Trader(symbols, 600)

while True:
    trader.live_trader()
    time.sleep(0.01)
