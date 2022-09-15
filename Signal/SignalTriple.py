import matplotlib.pyplot as plt
import numpy as np
def numpy_ewma_vectorized_v2(data, window):
    data = np.asarray(data)
    alpha = 2 /(window + 1.0)
    alpha_rev = 1-alpha
    n = data.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = data[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = data*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    return out

def time_series_embedding(data, delay=1, dimension=2):
    "This function returns the Takens embedding of data with delay into dimension, delay*dimension must be < len(data)"
    if delay * dimension > len(data):
        raise NameError('Delay times dimension exceed length of data!')
    emd_ts = np.array([data[0:len(data) - delay * dimension]])
    for i in range(1, dimension):
        emd_ts = np.append(emd_ts, [data[i * delay:len(data) - delay * (dimension - i)]], axis=0)
    return emd_ts
def svd_smoother(time_series:np.ndarray , rank_svd:int = 4, emb_dim:int = 10):
    emb = time_series_embedding(time_series,delay=1,dimension=emb_dim)
    u, s, v_h = np.linalg.svd(emb, full_matrices=False)
    u_r, s_r, v_h_r = u[:, 0:rank_svd], s[0:rank_svd], v_h[0:rank_svd, :]

    xx = np.matmul(np.matmul(u_r, np.diag(s_r)), v_h_r)
    return xx[0,:]
class SignalTriple:
    def __init__(self,
                 symbols_ticks:dict,
                 indexes_ticks:dict,
                 ):
        self.symbols_ticks = symbols_ticks
        self.indexes_ticks = indexes_ticks

    def signal(self):
        signal = {}
        signal_svd = self._symbol_svd_signal()
        signal_volume = self._volume_imbalanced_signal()
        for sym , pos_type in signal_svd.items():
            print(pos_type ,signal_volume[sym])
            if pos_type == signal_volume[sym]:
                signal[sym] = pos_type
            else:
                signal[sym] = 'HOLD'
        return signal

    def _symbol_svd_signal(self):
        signals = {}
        for symbol , ticks in self.symbols_ticks.items():
            ask = ticks['ask']
            s_ask = svd_smoother(ask, rank_svd=1, emb_dim=100)

            bid = ticks['bid']
            s_bid = svd_smoother(bid, rank_svd=1, emb_dim=100)
            if ask[0] - s_ask[0] > 10e-5:
                signals[symbol] = 'SELL'
            elif bid[0] - s_bid[0] < -10e-5:
                signals[symbol] = 'BUY'
            else:
                signals[symbol] = 'HOLD'
        return signals



    def _volume_imbalanced_signal(self):
        signals = {}
        for symbol, ticks in self.symbols_ticks.items():
            ask = ticks['ask']
            ask_size = ticks['ask_size']
            imb_ask = self.calculate_volume_imbalanced(ask, ask_size)

            bid = ticks['bid']
            bid_size = ticks['bid_size']
            imb_bid = self.calculate_volume_imbalanced(bid, bid_size)
            # print(imb_bid , imb_ask)

            # print((imb_bid - imb_ask )/(imb_bid + imb_ask))
            v_imb = (imb_bid) / (imb_bid + imb_ask)
            if v_imb > 0.75:
                # print('BUY')
                signals[symbol] = 'BUY'
            elif v_imb < 0.25:
                signals[symbol] = 'SELL'
            else:
                signals[symbol] = 'HOLD'
                # print('SELL')
        return signals

    @staticmethod
    def calculate_volume_imbalanced(time_series:np.ndarray,volume:np.ndarray):
        imb_volume = 0.
        last_volume = volume[0]
        imb_volume += last_volume

        for i , tick in enumerate(time_series):
            if np.isclose(tick,time_series[0],rtol=5e-5,atol=5e-6):

                if last_volume != volume[i]:

                    imb_volume += volume[i]
            else:
                break
        #print(time_series[0],imb_volume)
        return imb_volume

