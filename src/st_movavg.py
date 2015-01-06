import math
import pandas as pd

class st_movavg:
    def __init__(self,bt):
        self.stname = "movavg" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()


    def setup(self,win):
        self.win = win        
        print "========ST_MOVAVG SETUP ========================================"
        print "window",self.win
        print "================================================================"

    def getStrategyName(self):
        return self.stname
        
    def process(self,bt,symbol,param,ohlc_px,spy_px):        
        #different approach        
        if param['mode']=='1':
            #self.processOptimization(symbol,ohlc_px,spy_px)
            return None
        elif param['mode']==None or param['mode']=='0':            
            #self.setup(win)
            dv = self.processAllPriceData(ohlc_px)
            print dv
            return dv
        return None

    def procSingleData(self,index,price):
        mvg = self.dfmv[200].iloc[index]
        if price>=mvg:
            self.tradesup.buyorder(self.stname)
            print "mvg buy@",index,price
        elif price < mvg:
            self.tradesup.sellorder(self.stname)
            #self.tradesup.holdorder(self.stname)
            print "mvg sell@",index,price
        return
        
    def processAllPriceData(self,ohlc):
        self.tradesup.setup(ohlc,10000)
        self.dfmv = pd.DataFrame(index=ohlc.index)
        mvlst=[5,10,20,50,100,200]
        close_px = ohlc['Adj Close']  
        for idx in mvlst:
            self.dfmv[idx] = pd.rolling_mean(close_px, idx)
        
        return self.dfmv
        