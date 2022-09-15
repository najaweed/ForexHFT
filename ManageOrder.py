import MetaTrader5 as mt5

if not mt5.initialize():
    print("initialize() failed, error code =",mt5.last_error())
    quit()


class ManageOrders:
    def __init__(self,
                 symbols,
                 ):
        self.symbols = symbols


    @staticmethod
    def _open_new_position(symbol, signal):
        deal_type = 0.
        deal_price = 0.
        if signal == 'BUY':
            deal_price = mt5.symbol_info_tick(symbol).bid
            deal_type = mt5.ORDER_TYPE_BUY
        elif signal == 'SELL':
            deal_price = mt5.symbol_info_tick(symbol).ask
            deal_type = mt5.ORDER_TYPE_SELL

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 0.01,
            "type": deal_type,
            "price": deal_price,
            "deviation": 0,
            "magic": 666,
            "type_time": mt5.ORDER_TIME_GTC,
            # "type_filling": mt5.ORDER_FILLING_RETURN,
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

    def _manage_signal_request_type(self,last_position_state:dict, new_signal_request: dict) -> dict:
        symbols_signals = {}
        for symbol in self.symbols:
            if new_signal_request[symbol] == 'CLOSE':
                symbols_signals[symbol] = 'CLOSE'

            elif new_signal_request[symbol] == 'BUY':
                if last_position_state[symbol] == 'CLOSE':
                    symbols_signals[symbol] = 'BUY'
                elif last_position_state[symbol] == 'SELL':
                    symbols_signals[symbol] = 'CLOSE'
                elif last_position_state[symbol] == 'BUY':
                    symbols_signals[symbol] = 'HOLD_BUY'

            elif new_signal_request[symbol] == 'SELL':
                if last_position_state[symbol] == 'CLOSE':
                    symbols_signals[symbol] = 'SELL'
                elif last_position_state[symbol] == 'SELL':
                    symbols_signals[symbol] = 'HOLD_SELL'
                elif last_position_state[symbol] == 'BUY':
                    symbols_signals[symbol] = 'CLOSE'

        return symbols_signals

    def manage_orders(self, last_position_state:dict,new_signal_request: dict):
        signals = self._manage_signal_request_type(last_position_state,new_signal_request)
        for symbol, signal in signals.items():

            if signal == 'CLOSE':
                self._close_opened_position(symbol)
            elif signal == 'BUY' or signal == 'SELL':
                if len(mt5.positions_get(symbol=symbol)) == 0:
                    self._open_new_position(symbol, signal)
            else:
                pass
                #self.last_requests[symbol] = self._get_opened_requests()[symbol]

            #self.last_requests = self._get_opened_requests()