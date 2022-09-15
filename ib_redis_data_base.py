from ib_insync import *
import numpy as np

import redis

db_redis = redis.Redis()
# db_redis.lpush('EURUSD','111,111,111')
# db_redis.lpush('EURUSD','2,111,111')
# db_redis.lpush('EURUSD','333,111,111')
#
# print(db_redis.lrange('EURUSD',0,10))
#
# util.startLoop()
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=16)
# sym = 'EURUSD'
# contract = Forex(sym)
# ib.qualifyContracts(contract)
# ticker = ib.reqMktDepth(contract, numRows=20)


from IPython.display import display, clear_output
import pandas as pd

contracts = [Forex(pair) for pair in ('EURUSD', 'EURGBP', 'GBPUSD')]
ib.qualifyContracts(*contracts)
for contract in contracts:
    ib.reqMktData(contract, '', False, False)


def onPendingTickers(tickers):
    for ticker in tickers:
        # columns = ['ask' , 'ask_size','bid','bid_size']
        if ticker.ask != -1 or ticker.bid != -1:
            db_redis.lpush(ticker.contract.pair(), f'{ticker.ask, ticker.askSize, ticker.bid, ticker.bidSize}')


ib.pendingTickersEvent += onPendingTickers
ib.sleep(1e10)
# print('000')
# ib.pendingTickersEvent -= onPendingTickers
