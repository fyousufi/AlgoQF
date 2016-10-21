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

class SimpleTrendsStrategy(Strategy):
    def __init__(self, bars, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        self.bought = self._calculate_initial_bought()

        self.g_sell_gain_thresh = 0
        self.g_sell_loss_thresh = 0
        self.g_buy_thresh = 0
        self.g_buy_again_thresh = 0
        self.g_incr = 0

        ##Take the current bar that met accepted value initially zero
        ##prev = -1 ##set to negative one if it has never been initialized

        ##Store the prev in a data structure in order to compare
        ##amongst various grouping of stocks and retain datastructure

        self.prev_bars = {}


    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=1)

            ## if prev is initial then obtain the first value
                if(s not in self.prev_bars):
                    self.prev_bars[s] = self.bars.get_first_bar(s, N=0)
                    prev = self.prev_bars[s][5]
                else:
                    prev = self.prev_bars[s][5]
                ##current

                curr = bars[0][5]

                ##delta value

                delta = curr- prev

                ## per change

                percent_change = delta/ prev



                if bars is not None and bars != []:
                    if self.bought[s] == True:
                        # (Symbol, Datetime, Type = LONG, SHORT, EXIT)
                        if percent_change > self.g_sell_gain_thresh:
                            signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                            self.events.put(signal)
                            time.sleep(0.01)
                            self.bought[s] = False
                            self.prev_bars[s][5] = curr

                        ##Add code to reset g_sell_gain_thresh/ or set it outside of block for each symbol

                        elif percent_change < self.g_sell_loss_thresh:
                            signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                            self.prev_bars[s][5] = curr
                            self.bought[s] = False

                            ##Add code to reset g_sell_loss_thresh/ or set it outside of block for each symbol

                        else:
                            pass
                    else:
                        if percent_change < self.g_buy_thresh or percent_change > self.g_buy_again_thresh:
                            signal = SignalEvent(bars[0][0], bars[0][1], 'LONG')
                            self.events.put(signal)
                            time.sleep(0.01)
                            self.prev_bars[s][5] = curr
                            self.bought[s] = True

                            ##Add code to reset g_buy_thresh and g_buy_again_thresh/ or set it outside of block for each symbol

                        else:
                            pass


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
                        time.sleep(0.01)
                        self.bought[s] = True
                    else:
                        signal = SignalEvent(bars[0][0], bars[0][1], 'EXIT')
                        self.events.put(signal)
                        time.sleep(0.01)
                        self.bought[s] = False
