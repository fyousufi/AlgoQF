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
        self.initial_bar_counter = 0

    def _open_convert_csv_files(self):
        """ convert csv files to pandas DataFrames """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.io.parsers.read_csv(
                        os.path.join(self.csv_dir, '%s.csv' % s),
                        header = 0, index_col = 0, usecols=[0,1,3,2,4,5,11],
                        names = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'Adj. Close']
                        ).iloc[::-1]

            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            self.latest_symbol_data[s] = []

    ##Architecture Note for .csv iteration from Pandas:
        ##Uncomment BELOW "for block" if you want the same date ticks to compare all symbols meaning if FB.csv has a bar from January 1, 2014, then all symbols GOOGL, AMZN etc will
        ##also be compared from this date, even if they don't have data on the exchange, they will be padded with 'na' values. This most likely doesn't make sense
        ## for our purposes so this will be commented out, unless some minute by minute strategy requires this tick by tick comparison in the future

        ##PADDING BELOW FOR UNIFORM TICK BY TICK COMPARISON (ALL SYMBOLS GET THE SAME DATE/TIME tick for comparision from time t )
        ##This section of the code is not viable for backtesting from Pandas and has to be inserted into Database like sqlite
        ##It could ONLY work for .csv calls to Quandl for day to day tick data every 15 or 30 minutes during the trading day ONLY
        ##Live Application ONLY FOR Live Trading (backtesting flag = FALSE)
        for s in self.symbol_list:
        #     self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()
        ## simply iterate through the df to creat the rows needed
            self.symbol_data[s] = self.symbol_data[s].iterrows()

## This is essentially what loops through your code, but since the csv files yields a tuple, we have to move through it with yield, one by one in the dataframe
    def _get_new_bar(self, symbol):
        for b in self.symbol_data[symbol]:
            ##print self.symbol_data['FB']
            # if type(b[0]) != 'datetime.date':
            #     next(self.symbol_data[symbol])

            # print type(self.initial_bar_counter.real)
            # if self.initial_bar_counter in [0,1,2,3,4,5,6,7,8,9]:
            #     place_dt = datetime.date.today().isoformat()
            #     self.initial_bar_counter = self.initial_bar_counter + 1
            #     print self.initial_bar_counter
            #     yield tuple([symbol, datetime.datetime.strptime(place_dt, '%Y-%m-%d').date(),# %H:%M:%S'),
            #             0, 0, 0, 0, 0])
            # else:
            #     print self.initial_bar_counter
                yield tuple([symbol, datetime.datetime.strptime(b[0], '%Y-%m-%d').date(),# %H:%M:%S'),
                        b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])

##Returns the most upto date bar in the dataset meaning the last line as the data comes in from new to old
    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set"
        else:
            ##print bars_list[-N:]
            return bars_list[-N:]
## Returns the first element of the list of bars simply to inititalize meaning the newest data but method no longer used will rely on zero value as initial price
    # def get_first_bar(self, symbol, N=0):
    #     try:
    #         ##bars_list = self.latest_symbol_data[symbol]
    #         ##for the first bar we want the first value from the symbol data which is in reverse order for this first initial step
    #         bars_list = self.symbol_data[symbol]
    #         print bars_list
    #     except KeyError, name:
    #             print ("That symbol is not available in the historical data set",name)
    #     else:
    #             return bars_list[N+1:N+2]


##Either update with a loop condition that loops through with the increment or
##Utilize a different indexing methods into Pandas data frame that iterrows which simply iterates into the frames
    def update_bars(self):
        for s in self.symbol_list:
            try:
                    bar = self._get_new_bar(s).next()
                    ##print bar
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())
        time.sleep(0.01)
        #print self.events.empty()
