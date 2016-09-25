class Event(object):
    """
    Base class for all events, will trigger further events
    """
    pass

class MarketEvent(Event):
    """
    Handles getting a new market update
    """
    def __init__(self):
        self.type = 'MARKET'

class SignalEvent(Event):
    """
    Handles sending a Signal from a Strategy Object.
    Received by Portfolio object and acted upon.
    """
    def __init__(self, symbol, datetime, signal_type, strength=1):
        self.type = 'SIGNAL'
        self.symbol = symbol # 'GOOG'
        self.datetime = datetime # timestamp of signal
        self.signal_type = signal_type # 'LONG' or 'SHORT'
        self.strength = strength

class OrderEvent(Event):
    """
    Handles sending Order to execution system.
    """
    def __init__(self, symbol, order_type, quantity, direction):
        self.type = 'ORDER'
        self.symbol = symbol
        self.order_type = order_type # 'MKT' or 'LMT'
        self.quantity = quantity
        self.direction = direction # 'BUY' or 'SELL'

    def print_order(self):
        print "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            (self.symbol, self.order_type, self.quantity, self.direction)

class FillEvent(Event):
    """
    Filled order returned from broker
    """
    def __init__(self, timeindex, symbol, exchange, quantity,
                 direction, fill_cost, commission=None):
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        if commission is None:
            self.commission = self.calculate_ib_commission()
        else:
            self.commission = commission

    def calculate_ib_commission(self):
        """
        TODO: Add a case for foreign exchange
        Based on "US API Directed Orders":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else:
            full_cost = max(1.3, 0.008 * self.quantity)
        full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        return full_cost
