import datetime
import os, os.path
import pandas as pd
import time

from abc import ABCMeta, abstractmethod

from event import MarketEvent

class DataHandler(object):
    """abstract class providing interface for subsequent data handlers"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """ Returns last N bars from latest_symbols list """
        raise NotImplementedError("get_latest_bars() is not implemented")

    def update_bars(self):
        """ Pushes latest bars to latest_symbols list """
        raise NotImplementedError("update_bars() is not implemented")

class HistoricCSVDataHandler(DataHandler):
    """ read CSV files for each requested symbol and provides latest bars """
    def __init__(self, events, csv_dir, symbol_list):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """ convert csv files to pandas DataFrames """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.io.parsers.read_csv(
                        os.path.join(self.csv_dir, '%s.csv' % s),
                        header = 0, index_col = 0, usecols=[0,1,3,2,4,5,11],
                        names = ['datetime', 'open', 'low', 'high', 'close', 'volume', 'Adj. Close']
                        ).iloc[::-1]

            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            self.latest_symbol_data[s] = []
        ##Uncomment BELOW "for block" if you want the same date ticks to compare all symbols meaning if FB.csv has a bar from January 1, 2014, then all symbols GOOGL, AMZN etc will
        ##also be compared from this date, even if they don't have data on the exchange, they will be padded with 'na' values. This most likely doesn't make sense
        ## for our purposes so this will be commented out, unless some minute by minute strategy requires this tick by tick comparison in the future

        ##PADDING BELOW FOR UNIFORM TICK BY TICK COMPARISON (ALL SYMBOLS GET THE SAME DATE/TIME tick for comparision from time t )

        # for s in self.symbol_list:
        #     self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

## This is essentially what loops through your code, but since the csv files yields a tuple, we have to move through it with yield, one by one in the dataframe
    def _get_new_bar(self, symbol):
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.datetime.strptime(b[0], '%Y-%m-%d'),# %H:%M:%S'),
                        b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])

##Returns the most upto date bar in the dataset meaning the last line as the data comes in from new to old
    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set"
        else:
            return bars_list[-N:]
## Returns the first element of the list of bars simply to inititalize meaning the newest data
    def get_first_bar(self, symbol, N=0):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError, name:
                print ("That symbol is not available in the historical data set",name)
        else:
                return bars_list[N:N+1]

##Either update with a loop condition that loops through with the increment or
##Utilize a different indexing methods into Pandas data frame that iterrows which simply iterates into the frames
    def update_bars(self):
        for s in self.symbol_list:
            try:
                bar = self._get_new_bar(s).next()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())
        time.sleep(0.01)
        #print self.events.empty()
