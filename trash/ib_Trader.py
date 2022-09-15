from ib_insync import *
import numpy as np

util.startLoop()
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=16)
sym = 'EURUSD'
contract = Forex(sym)
ib.qualifyContracts(contract)
ticker = ib.reqMktDepth(contract, numRows=20)


class MyBook:
    def __init__(self,
                 num_ticks: int = 4,
                 ):
        self.last_book = None
        self.num_ticks = num_ticks
        self.my_books = []

    def check_update(self, new_book):
        if self.last_book is None:
            self.last_book = new_book
            self.my_books.append(new_book)

        elif new_book != self.last_book:
            if len(self.my_books) < self.num_ticks:
                self.my_books.append(new_book)
                self.last_book = new_book
            elif len(self.my_books) >= self.num_ticks:
                self.my_books.append(new_book)
                self.my_books.pop(0)
                self.last_book = new_book

        return self.my_books

    @staticmethod
    def ib_ticker_to_book_info(ticker):
        bids = ticker.domBids
        bid_price = np.asarray([[bid.price, bid.size] for bid in bids])

        asks = ticker.domAsks
        ask_price = np.asarray([[ask.price, ask.size] for ask in asks])

        w_bid = np.round(np.average(bid_price[:, 0], weights=bid_price[:, 1]), decimals=5)
        w_ask = np.round(np.average(ask_price[:, 0], weights=ask_price[:, 1]), decimals=5)
        ask_low = np.min(ask_price[:, 0])
        ask_high = np.max(ask_price[:, 0])

        bid_low = np.min(bid_price[:, 0])
        bid_high = np.max(bid_price[:, 0])
        return {'ask_low': ask_low,
                'ask_avg': w_ask,
                'ask_high': ask_high,
                'ask_volume': np.sum(ask_price[:, 1]),
                #'ask_volume': ask_price[0, 1],

                #
                'bid_low': bid_low,
                'bid_avg': w_bid,
                'bid_high': bid_high,
                'bid_volume': np.sum(bid_price[:, 1]),
                #'bid_volume': bid_price[0, 1],

                #
                'spread_low': ask_low - bid_high,
                'spread_avg': w_ask - w_bid,
                'spread_high': ask_high - bid_low
                }


booker = MyBook(num_ticks=5)
from Signal.SingalVolume import volume_singal
from ManageOrder import ManageOrders
import MetaTrader5 as mt5
mo = ManageOrders([sym])
def _get_opened_requests(symbols) -> dict:
    symbols_requests = {}
    for symbol in symbols:
        positions = mt5.positions_get(symbol=symbol)
        if len(positions) > 0:
            if positions[0]._asdict()['type'] == 1:
                symbols_requests[symbol] = 'SELL'
            elif positions[0]._asdict()['type'] == 0:
                symbols_requests[symbol] = 'BUY'
        else:
            symbols_requests[symbol] = 'CLOSE'
    return symbols_requests


def onTickerUpdate(ticker):
    book_info = booker.ib_ticker_to_book_info(ticker)
    order_books = booker.check_update(book_info)

    if len(order_books) >= 5:
        new_signal = volume_singal(sym,order_books)
        last_req = _get_opened_requests([sym])
        mo.manage_orders(last_req,new_signal)

ticker.updateEvent += onTickerUpdate

IB.sleep(1e10)
