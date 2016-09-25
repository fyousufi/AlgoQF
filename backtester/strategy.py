import datetime
import numpy as np
import pandas as pd
import time
import Queue

from abc import ABCMeta, abstractmethod

from event import SignalEvent

class Strategy(object):
    """
        Base class, derived Strategy objects will generate signals for symbols
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("calculate_signals() is not implemented")

class BuyAndHoldStrategy(Strategy):
    "Example strategy that goes LONG on all the symbols"
    def __init__(self, bars, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        # (Symbol, Datetime, Type = LONG, SHORT, EXIT)
                        signal = SignalEvent(bars[0][0], bars[0][1], 'LONG')
                        self.events.put(signal)
                        time.sleep(0.1)
                        self.bought[s] = True
                    else:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                        self.events.put(signal)
                        time.sleep(0.1)
                        self.bought[s] = False
