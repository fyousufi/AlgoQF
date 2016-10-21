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
    symbol_list=['FB', 'AAPL','GOOG']

    ##Ensures person executes this tester on a Linux or Mac or uses a VM
    if platform.system() not in ['Linux', 'Darwin']:
        print "Program must run on Linux/Unix system or on Virtual Machine running such a system, please run again"
        quit()

    ##ensure you are logged into session at quandl or set the api key, but for WIKI dataset not necessary
    ##Below URL will be modifed to obtain futures dataset
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


    bars = HistoricCSVDataHandler(events, ab_path + '/', symbol_list)
    ##strategy = BuyAndHoldStrategy(bars, events)
    ##strategy for simple trends, this variable must be set as a list to test multiple strategies etc.


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
if __name__ == '__main__':
    simulate()
