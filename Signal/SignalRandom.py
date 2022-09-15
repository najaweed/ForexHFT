import numpy as np

class SignalRandom:
    def __init__(self,
                 step_input:dict
                 ):
        self.step_input = step_input

    def signal(self):
        signal = {}
        for symbol, rates  in self.step_input.items():
              signal[symbol] = np.random.choice(['SELL','HOLD','BUY'])
        return signal


