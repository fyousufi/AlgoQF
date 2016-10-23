# Declare the components with respective parameters
from data import HistoricCSVDataHandler
from strategy import BuyAndHoldStrategy
from strategy import SimpleTrendsStrategy
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler
try:
    import Queue as queue
except ImportError:
    import queue
import time
import platform
import csv
import requests
import os
import urllib
import calendar
import time

def simulate():
    events = queue.Queue()

    ##Set this directory as the one where you will store the .csv files by ticker symbol ex. FB.csv etc it will be named from root
    ##so a directory in your home folder might be /home/data where /data is the folder with the files

    directory = '/twoterradata'
    ab_path = os.path.abspath(directory)
    ##Below symbol list for stocks
    ##Could be modified for Futures
    symbol_list=['FB', 'AAPL','GOOG']

    ##list of thresholds to be set initially for each stock/futures symbols and passed in to the strategy class
    # self.g_sell_gain_thresh = 0
    # self.g_sell_loss_thresh = 0
    # self.g_buy_thresh = 0
    # self.g_buy_again_thresh = 0
    # g_incr is the
    global_thresholds = {'g_sell_gain_thresh':0,'g_sell_loss_thresh':0,'g_buy_thresh':0,'g_buy_again_thresh':0,'g_incr':0}
    symbol_thresholds={}
    for s in symbol_list:
        symbol_thresholds[s] = global_thresholds


    ##Futures_list --would have to update code or use the current symbol_list variable modified for Futures

    ##Define these global thresholds for each value in the symbol

    ##Ensures person executes this tester on a Linux or Mac or uses a VM
    if platform.system() not in ['Linux', 'Darwin']:
        print "Program must run on Linux/Unix system or on Virtual Machine running such a system, please run again"
        quit()

    ##ensure you are logged into session at quandl or set the api key, but for WIKI dataset not necessary
    ##Below URL will be modifed to obtain futures dataset and most likely will be modified with database queries
    quandl_url = "\'https://www.quandl.com/api/v3/datasets/WIKI/"
    for s in symbol_list:
        if os.path.exists(ab_path+'/'+s+'.csv'):
            days_modified = (calendar.timegm(time.gmtime())-os.path.getmtime(ab_path+'/'+s+'.csv'))
            if days_modified > 86400:
                cmd = "curl "  + quandl_url + s + "/data.csv\'" + "> \'" + ab_path + '/' + s + ".csv\'"
                os.system(cmd)
        else:
            cmd = "curl "  + quandl_url + s + "/data.csv\'" + "> \'" + ab_path + '/' + s + ".csv\'"
            os.system(cmd)

    print symbol_thresholds

    bars = HistoricCSVDataHandler(events, ab_path + '/', symbol_list)
    ##strategy = BuyAndHoldStrategy(bars, events)
    ##strategy for simple trends, this variable must be set as a list to test multiple strategies etc.

    ## Set strategy by modifying here
    strategy= SimpleTrendsStrategy(bars,events)
    port = NaivePortfolio(bars, events, "2015-11-18")
    broker = SimulatedExecutionHandler(events)

    while True:
        # Update the bars (specific backtest code, as opposed to live trading)
        if bars.continue_backtest == True:
            bars.update_bars()
        else:
            break

        # Handle the events
        while True:
            try:
                event = events.get(False)
            except queue.Empty:
                break
            else:
                if event is not None:
                    if event.type == 'MARKET':
                        strategy.calculate_signals(event)
                        port.update_timeindex(event)
                    elif event.type == 'SIGNAL':
                        port.update_signal(event)
                    elif event.type == 'ORDER':
                        #event.print_order()
                        broker.execute_order(event)
                    elif event.type == 'FILL':
                        port.update_fill(event)

    print port.output_summary_stats()
    print port.all_holdings[-1]
    ##The below means we will only run this directly if backtester.py is called on its own (python will set this as main), else if our
    ##entire program backtester/. is a component in a larger program, we will have to execute backtester.simulate() within that program
if __name__ == '__main__':
    simulate()
