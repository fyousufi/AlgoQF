from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, message

#ib_api_demo

def error_handler(msg):
    "Handle capturing errors message"
    print "Server Error: %s" % msg

def reply_handler(msg):
    "Handler of server reply"
    print "server Response: %s, %s" % (msg.typeName, msg)

def create_contract(symbol, sec_type, exch, prim_exch, curr):
    "Create object that will be a contract and exchange and currency"
    "symbol is the ticker symbol of security"
    "sec type security type of contract"
    "prim_exch is the primary exchange vs the excahnge which is simply exchange"
    "currency is cur"
    "fields initialized below"
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr

    return contract

def create_order(order_type, quantity, action):
    "Create an Order Object (Market/Limit) to go long/short"

    "order type- 'MKT', 'LMT', etc - MIT, LIT, TLT, all order types we have learned "
    "quantity- how many you want to buy or sell, remember than options are 1 (for each 100 shares of stocks/ multiply price by 100 of the option)"

    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order


# ib_api_demo.py

if __name__ == "__main__":
    # Connect to the Trader Workstation (TWS) running on the
    # usual port of 7496, with a clientId of 100
    # (The clientId is chosen by us and we will need
    # separate IDs for both the execution connection and
    # market data connection)
    tws_conn = Connection.create(port=7496, clientId=100)
    tws_conn.connect()

    # Assign the error handling function defined above
    # to the TWS connection
    tws_conn.register(error_handler, 'Error')

    # Assign all of the server reply messages to the
    # reply_handler function defined above
    tws_conn.registerAll(reply_handler)

    # Create an order ID which is 'global' for this session. This
    # will need incrementing once new orders are submitted.
    order_id = 1

    # Create a contract in GOOG stock via SMART order routing
    goog_contract = create_contract('GOOG', 'STK', 'SMART', 'SMART', 'USD')

    # Go long 100 shares of Google
    goog_order = create_order('MKT', 100, 'BUY')

    # Use the connection to the send the order to IB
    tws_conn.placeOrder(order_id, goog_contract, goog_order)

    # Disconnect from TWS
    tws_conn.disconnect()
