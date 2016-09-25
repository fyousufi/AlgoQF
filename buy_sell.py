from __future__ import division
import csv
import requests
import itertools
from numpy import arange
import math

def main():
    #yahoo_url = "http://chart.finance.yahoo.com/table.csv?"
    #params = "s=FB"
    yahoo_url = "http://chart.finance.yahoo.com/table.csv?s=FB&a=0&b=1&c=1980&d=11&e=31&f=2016&g=w"
    data = requests.get(yahoo_url).content

    data_lines = data.splitlines()
    incr = 1
    header = data_lines.pop(0)
    data_lines = list(reversed(data_lines))

    data_skipped = [data_lines[i] for i in range(len(data_lines)) if i % incr == 0 ]
    data_skipped.insert(0, header)
    cr = csv.DictReader(data_skipped)
    own = False
    num_shares = 100
    port_val = 100000
    stocks_val = 0
    for row in cr:
        #print '\n', row['Date'], row['Adj Close']
        curr = float(row['Adj Close'])
        if own:
            #print "SELL, you have gained %f" % (percent_change)
            own = False
            port_val += curr * num_shares
            stocks_val = 0
        else:
            #print "buy, stock is down/up by ", percent_change
            #num_shares = math.floor(port_val / curr)
            own = True
            port_val -= curr * num_shares
            stocks_val += curr * num_shares

    print port_val
    print stocks_val
    print port_val + stocks_val
if __name__ == '__main__':
    main()
