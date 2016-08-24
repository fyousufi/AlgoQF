from __future__ import division
import csv
import requests

def main():
    yahoo_url = "http://chart.finance.yahoo.com/table.csv?"
    params = "s=FB"
    data = requests.get(yahoo_url + params).content

    data_lines = data.splitlines()
    incr = 2
    header = data_lines.pop(0)
    data_lines = list(reversed(data_lines))
    data_skipped = [data_lines[i] for i in range(len(data_lines) - 1) if i % incr == 0 ]
    data_skipped.insert(0, header)

    cr = csv.DictReader(data_skipped)

    sell_gain_thresh = .5
    sell_loss_thresh = -0.05
    buy_thresh = -0.2
    buy_again_thresh = 0.1
    own = True
    first = cr.next()
    prev = float(first['Adj Close'])
    init = prev
    net = -prev
    print first['Date'], prev
    for row in cr:
        print '\n', row['Date'], row['Adj Close']
        curr = float(row['Adj Close'])
        delta = curr - prev
        updated_init = init + delta
        percent_change = (updated_init - init) / init
        if own:
            if percent_change > sell_gain_thresh:
                print "sell, you have gained ", percent_change
                prev = curr
                init = curr
                own = False
                net += updated_init
            elif percent_change < sell_loss_thresh:
                print "sell, you have lost ", percent_change
                prev = curr
                init = curr
                own = False
                net += delta
            else:
                print "keep, not enough change this week ", percent_change
        else:
            if percent_change < buy_thresh or percent_change > buy_again_thresh:
                print "buy, stock is down/up by ", percent_change
                init = curr
                prev = curr
                init = updated_init
                own = True
            else:
                print "don't buy, not enough change this week ", percent_change
        print 'init ', init, 'delta ', delta

    print net

if __name__ == '__main__':
    main()
