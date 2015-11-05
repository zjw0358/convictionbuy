from time import sleep, strftime
from time import sleep
from ib.ext.Contract import Contract
from ib.opt import ibConnection, message

def my_account_handler(msg):
    print(msg)


def my_tick_handler(msg):
    print(msg)
    
def my_hist_data_handler(msg):
    print(msg)

if __name__ == '__main__':
    con = ibConnection()
    con.register(my_hist_data_handler, message.historicalData)
    #con.register(my_account_handler, 'UpdateAccountValue')
    #con.register(my_tick_handler, message.tickSize, message.tickPrice)
    con.connect()

    def inner():

        qqqq = Contract()
        qqqq.m_secType = "STK" 
        #qqqq.m_secType = "CASH" 
        #qqqq.m_symbol = "EUR.USD"
        qqqq.m_symbol = "AAPL"
        qqqq.m_currency = "USD"
        qqqq.m_exchange = "SMART" #for stocks usually
        qqqq.m_primaryExch = "SMART"
        #qqqq.m_exchange = "IDEALPRO"
        #qqqq.m_exchange = "ISLAND"
        
        endtime = strftime('%Y%m%d %H:%M:%S')
        print endtime,"========="
        #con.reqHistoricalData(1,qqqq,endtime,"5 D","1 hour","MIDPOINT",1,1)
        con.reqHistoricalData(1,qqqq,endtime,"1 M","1 day","TRADES",1,1)
        #con.reqHistoricalData(1,qqqq,endtime,"1 D","1 year","MIDPOINT",1,1)
        print con
        sleep(10)

    inner()
    sleep(5)
    print('disconnected', con.disconnect())
    