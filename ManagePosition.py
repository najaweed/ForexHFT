import MetaTrader5 as mt5

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()


class ManagePositions:
    def __init__(self,
                 symbols: list,
                 # config: dict,
                 ):
        self.symbols = symbols
        # self.config = config
        self.max_stop_loss_price = {}

    def _set_stop_loss(self, position, price_stop_loss=None):
        sl_price = 0

        book = None
        if price_stop_loss is None:
            book = self._get_market_book_rates(position['symbol'])
        if position['type'] == mt5.ORDER_TYPE_SELL:
            if price_stop_loss is not None:
                sl_price = price_stop_loss
            elif price_stop_loss is None:
                sl_price = book['ask_high'] + book['spread_low']/1
                self.max_stop_loss_price[position['symbol']] = sl_price


        elif position['type'] == mt5.ORDER_TYPE_BUY:
            if price_stop_loss is not None:
                sl_price = price_stop_loss
            elif price_stop_loss is None:
                sl_price = book['bid_low'] - book['spread_low']/1
                self.max_stop_loss_price[position['symbol']] = sl_price


        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position['symbol'],
            "position": position['ticket'],
            "sl": sl_price,
            # "tp": tp_price,
        }
        mt5.order_send(request)

    @staticmethod
    def _close_opened_position(symbol):
        positions = mt5.positions_get(symbol=symbol)
        if len(positions) > 0:
            for position in positions:
                position = position._asdict()
                deal_type = 0.
                deal_price = 0.
                #print(position)
                if position['type'] == mt5.ORDER_TYPE_BUY:
                    deal_type = mt5.ORDER_TYPE_SELL
                    deal_price = mt5.symbol_info_tick(symbol).ask
                elif position['type'] == mt5.ORDER_TYPE_SELL:
                    deal_type = mt5.ORDER_TYPE_BUY
                    deal_price = mt5.symbol_info_tick(symbol).bid

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": position['volume'],
                    "type": deal_type,
                    "position": position['ticket'],
                    "price": deal_price,
                    "deviation": 0,
                    "magic": 666,
                    "comment": "python script close",
                    "type_time": mt5.ORDER_TIME_SPECIFIED,
                    # "type_filling": mt5.ORDER_FILLING_IOC,
                }
                mt5.order_send(request)

    @staticmethod
    def _get_market_book_rates(symbol):
        asks, bids = [], []
        if mt5.market_book_add(symbol):
            books = mt5.market_book_get(symbol)
            if books is not None:
                for book in books:
                    book = book._asdict()
                    if book['type'] == 1:
                        asks.append(book['price'])
                    elif book['type'] == 2:
                        bids.append(book['price'])

                return {'ask_high': max(asks), 'ask_low': min(asks),
                        'bid_high': max(bids), 'bid_low': min(bids),
                        'spread_high': max(asks) - min(bids),
                        'spread_low': min(asks) - max(bids)}

    def _trail_stop_loss(self, position):
        order_book = self._get_market_book_rates(position['symbol'])

        if position['type'] == mt5.ORDER_TYPE_SELL:
            if order_book['ask_high'] < position['sl']:
                new_price_stop_loss = order_book['ask_high'] + order_book['spread_high']/1
                if new_price_stop_loss < self.max_stop_loss_price[position['symbol']]:
                    self._set_stop_loss(position, new_price_stop_loss)

        elif position['type'] == mt5.ORDER_TYPE_BUY:
            if order_book['bid_low'] > position['sl']:
                new_price_stop_loss = order_book['bid_low']- order_book['spread_high']/1
                if new_price_stop_loss > self.max_stop_loss_price[position['symbol']]:

                    self._set_stop_loss(position, new_price_stop_loss)

    def _take_profit(self, position):
        #print(position['profit'])
        # if position['profit'] >= 0.05:
        #     self.max_stop_loss_price[position['symbol']] = position['price_open']
            #self._close_opened_position(position['symbol'])
        if position['profit'] >= 0.07 :
             self._close_opened_position(position['symbol'])




    def manage_positions(self):
        print(self.max_stop_loss_price)
        for symbol in self.symbols:
            positions = mt5.positions_get(symbol=symbol)
            if len(positions) > 0:
                for position in positions:
                    position = position._asdict()
                    #
                    if position['sl'] == 0:
                        self._set_stop_loss(position)
                    #
                    self._trail_stop_loss(position)
                    #
                    self._take_profit(position)
