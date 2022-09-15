class SpikeTrader:
    def __init__(self,
                 step_dict_df: dict,
                 step_book_order: dict
                 ):
        self.step_dict_df = step_dict_df
        self.step_book_order = step_book_order
        self.thresholds = self._get_thresholds()

    def _get_thresholds(self):
        thresholds = {}
        for symbol, book in self.step_book_order.items():
            thresholds[symbol] = book['spread_high']
        return thresholds

    def signal(self):
        signal = {}
        for symbol, df in self.step_dict_df.items():
            signal[symbol] = self._gen_signal(symbol, df)
        return signal
    def _gen_signal(self, symbol, df):

        if self.buy_spike(df.ask, self.thresholds[symbol])/1:
            return 'BUY'
        elif self.sell_spike(df.bid, self.thresholds[symbol]/1):
            return 'SELL'
        else:
            return 'HOLD'

    @staticmethod
    def sell_spike(ticks_bid, pull_back_threshold):
        threshold = 0
        diff_bid = ticks_bid.diff().tail(20).to_numpy()
        for x in reversed(diff_bid):
            if x > 0:
                threshold = 0
            elif x <= 0:
                threshold += x
            if threshold < -pull_back_threshold:
                return True
        return False

    @staticmethod
    def buy_spike(ticks_ask, pull_back_threshold):
        threshold = 0
        diff_ask = ticks_ask.diff().tail(20).to_numpy()
        for x in reversed(diff_ask):
            if x < 0:
                threshold = 0
            elif x >= 0:
                threshold += x
            if threshold > pull_back_threshold:
                return True
            #print(threshold ,pull_back_threshold)
        return False


# from LiveMarket import LiveMarket
#
# symbols = ['EURUSD', 'EURGBP', 'GBPUSD']
# live_market = LiveMarket(symbols)
# rates = live_market.get_symbol_rates()
# books = live_market.get_order_books()
#
# print(SpikeTrader(rates, books).signal())
