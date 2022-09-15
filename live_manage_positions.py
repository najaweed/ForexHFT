import time

from ManagePosition import ManagePositions
import MetaTrader5 as mt5

if not mt5.initialize():
    print("initialize() failed, error code =", mt5.last_error())
    quit()

symbols = ['EURUSD', 'EURGBP','GBPUSD']
mp = ManagePositions(symbols)
while True:
    mp.manage_positions()
    time.sleep(0.001)