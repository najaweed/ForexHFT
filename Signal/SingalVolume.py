class VolumeImbalanced:
    def __init__(self,
                 order_books: list,
                 ):
        self.books = order_books


    def signal(self):

        d_volume_ask = self._calculate_delta_ask_orders()
        d_volume_bid = self._calculate_delta_bid_orders()
        diff = d_volume_bid - d_volume_ask
        if diff !=0:
            diff /= (d_volume_bid + d_volume_ask)
        return diff
    def _calculate_delta_bid_orders(self):
        book_2 = self.books[-1]
        book_1 = self.books[-2]
        if book_1['bid_high'] > book_2['bid_high']:
            return 0.0
        elif book_1['bid_high'] == book_2['bid_high']:
            return book_2['bid_volume'] - book_2['bid_volume']
        elif book_1['bid_high'] < book_2['bid_high']:
            return book_2['bid_volume']

    def _calculate_delta_ask_orders(self):
        book_2 = self.books[-1]
        book_1 = self.books[-2]
        if book_1['ask_low'] < book_2['ask_low']:
            return 0.0
        elif book_1['ask_low'] == book_2['ask_low']:
            return book_2['ask_volume'] - book_2['ask_volume']
        elif book_1['ask_low'] > book_2['ask_low']:
            return book_2['bid_volume']


class VolumeRangeImbalanced:
    def __init__(self,
                 order_books: list,
                 ):
        self.books = order_books

    def signal(self):
        #print(self._calculate_imbalanced())
        return self._calculate_imbalanced()

    def _calculate_imbalanced(self):
        v_ask ,v_bid = 0.0 , 0.0
        for book in self.books:
            v_ask += book['ask_volume']
            v_bid += book['bid_volume']

        v_imbalanced = (v_bid - v_ask)/(v_bid + v_ask)

        return v_imbalanced


def volume_singal(symbol,order_books):
    imb_signal = VolumeRangeImbalanced(order_books).signal()
    v_signal = VolumeImbalanced(order_books).signal()
    if imb_signal > 0.14 and v_signal > 0:
        return {symbol:'BUY'}
    elif imb_signal < -0.14 and v_signal < 0:
        return {symbol: 'SELL'}

    else:
        return {symbol: 'HOLD'}

