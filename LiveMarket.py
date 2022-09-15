import math

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import pytz
timezone = pytz.timezone("Etc/GMT-3")

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


class LiveMarket:
    def __init__(self,
                 symbols: list,
                 ):
        self.symbols = symbols
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

    def _get_order_book(self, symbol: str):
        asks, bids = [], []
        volume_ask, volume_bid = [], []
        if mt5.market_book_add(symbol):
            books = mt5.market_book_get(symbol)
            if books is not None:
                for book in books:
                    book = book._asdict()
                    if book['type'] == 1:
                        asks.append(book['price'])
                        volume_ask.append((book['volume']))

                    elif book['type'] == 2:
                        bids.append(book['price'])
                        volume_bid.append(book['volume'])

                return {'ask_high': max(asks), 'ask_low': min(asks),
                        'bid_high': max(bids), 'bid_low': min(bids),
                        'ask_volume': sum(volume_ask),
                        'bid_volume': sum(volume_bid),
                        'spread_high': max(asks) - min(bids),
                        'spread_low': min(asks) - max(bids)}

    def _get_range_order_book(self, symbol: str, tick_shift: int = 1):
        range_order_books = []
        while len(range_order_books) < tick_shift:
            if len(range_order_books) == 0:
                range_order_books.append(self._get_order_book(symbol))
            elif len(range_order_books) >= 0:
                new_book = self._get_order_book(symbol)
                if new_book != range_order_books[-1]:
                    range_order_books.append(new_book)
        return range_order_books


    def get_order_books(self):
        order_books = {}
        for symbol in self.symbols:
            order_books[symbol] = self._get_order_book(symbol)
        return order_books

    def get_index_rates(self):
        order_books = self.get_order_books()
        index_rates = {cur: [1.0, 1.0] for cur in self.currencies}
        for symbol, books in order_books.items():
            for i, book in enumerate(books):
                cur_1, cur_2 = symbol[:3], symbol[3:]
                index_rates[cur_1][i] *= book['bid_high']#math.log(book['bid_high'])
                index_rates[cur_2][i] /= book['ask_low']#math.log(book['ask_low'])
        return index_rates

    def _get_live_tick(self,symbol, time_shift=1):
        time_from = datetime.now(tz=timezone) - timedelta(minutes=time_shift)
        ticks = mt5.copy_ticks_from(symbol, time_from, 100000, mt5.COPY_TICKS_ALL)
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
        ticks_frame = ticks_frame.set_index('time')
        last_ticks_index = ticks_frame.index[-1] - timedelta(minutes=time_shift)
        return ticks_frame.loc[last_ticks_index:, :]

    def get_symbol_rates(self):
        rates = {}
        for symbol in self.symbols:
            rates[symbol] = self._get_live_tick(symbol)
        return rates
