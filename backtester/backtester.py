# Declare the components with respective parameters
from data import HistoricCSVDataHandler
from strategy import BuyAndHoldStrategy
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler
try:
    import Queue as queue
except ImportError:
    import queue
import time

def simulate():
    events = queue.Queue()
    bars = HistoricCSVDataHandler(events, "backtester/", ['FB'])
    strategy = BuyAndHoldStrategy(bars, events)
    port = NaivePortfolio(bars, events, "2012-5-18")
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
    print port.current_holdings
    print port.current_positions
if __name__ == '__main__':
    simulate()
