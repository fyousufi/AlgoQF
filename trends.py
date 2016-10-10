from __future__ import division
import csv
import requests
import itertools
from numpy import arange

def main():
    yahoo_url = "http://chart.finance.yahoo.com/table.csv?"
    params = "s=FB"
    yahoo_url = "http://chart.finance.yahoo.com/table.csv?s=ORC.BE&a=0&b=1&c=2012&d=11&e=31&f=2012&g=d"
    data = requests.get(yahoo_url).content
    print "running"
    data_lines = data.splitlines()
    incr = 5
    header = data_lines.pop(0)
    data_lines = list(reversed(data_lines))

    g_sell_gain_thresh = 0
    g_sell_loss_thresh = 0
    g_buy_thresh = 0
    g_buy_again_thresh = 0
    g_incr = 0
    max_port = 0
    for incr, sell_gain_thresh, sell_loss_thresh, buy_thresh, buy_again_thresh in itertools.product(arange(1, 10, 1), arange(0.05, 1.0, 0.05), arange(-0.05, -1.0, -0.05), arange(-0.05, -1.0, -0.05), arange(0.05, 1.0, 0.05)):
        data_skipped = [data_lines[i] for i in range(len(data_lines) - 1) if i % incr == 0 ]
        data_skipped.insert(0, header)
        cr = csv.DictReader(data_skipped)
        own = True
        first = cr.next()
        prev = float(first['Adj Close'])
        num_shares = 53
        port_val = prev * num_shares
        initial_val = port_val
        ##print first['Date'], prev
        for row in cr:
            ##print '\n', row['Date'], row['Adj Close']
            curr = float(row['Adj Close'])
            delta = curr - prev
            percent_change = delta / prev
            if own:
                if percent_change > sell_gain_thresh:
                    print "SELL, you have gained %f" % (percent_change)
                    prev = curr
                    own = False
                    port_val = curr * num_shares
                    num_shares = 0
                elif percent_change < sell_loss_thresh:
                    print "SELL, you have lost %f" % (percent_change)
                    prev = curr
                    own = False
                    port_val = curr * num_shares
                    num_shares = 0
                else:
                    pass
                    ##print "KEEP, not enough change this week ", percent_change
            else:
                if percent_change < buy_thresh or percent_change > buy_again_thresh:
                    print "buy, stock is down/up by ", percent_change
                    prev = curr
                    own = True
                    num_shares = port_val / curr
                    port_val = curr * num_shares
                else:
                    pass
                    ##print "DON'T BUY, not enough change this week ", percent_change
        if port_val > max_port:
            max_port = port_val
            g_incr = incr
            g_sell_gain_thresh = sell_gain_thresh
            g_sell_loss_thresh = sell_loss_thresh
            g_buy_thresh = buy_thresh
            g_buy_again_thresh = buy_again_thresh

    print max_port
    print incr
    print g_sell_gain_thresh
    print g_sell_loss_thresh
    print g_buy_thresh
    print g_buy_again_thresh

if __name__ == '__main__':
    main()
