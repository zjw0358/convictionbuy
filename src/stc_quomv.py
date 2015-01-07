import pandas as pd
import st_quotient
import st_movavg

class stc_quomv:
    def __init__(self,bt):
        self.stname = "comb_quomv" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        #this strategy is consist of two strateges
        self.quo = st_quotient.st_quotient(bt)
        self.mvg = st_movavg.st_movavg(bt)
            
    def setup(self,win):
        self.win = win        
        print "========STC_QUOMV SETUP ========================================"
        print "window",self.win
        print "================================================================"
        
    def process(self,bt,symbol,param,ohlc_px,spy_px):
        # parameter
        k1 = 0.7
        k2 = 0.4
        cl = 25
        
        #setup component
        self.tradesup.addStrategy(self.quo.getStrategyName())
        self.tradesup.addStrategy(self.mvg.getStrategyName())
        
        #different approach        
        if param['mode']=='1':
            #self.processOptimization(symbol,ohlc_px,spy_px)
            return None
        elif param['mode']==None or param['mode']=='0':            
            self.mvg.cleanup()
            #self.setup(win)
            self.quo.setup(k1,k2,cl)
            #self.mvg.addMApair(200,50)            
            self.mvg.addPxCrossMa(200)
            self.mvg.setup()
            dv = self.processAllPriceData(ohlc_px)
            print dv
            return dv
        return None
        
    def processAllPriceData(self,ohlc):
        self.tradesup.setup(ohlc,10000)
        close_px = ohlc['Adj Close']  
        self.mvg.processAllPriceData(ohlc)


        for index in range(0, len(close_px)):
            self.tradesup.processData(index)  #must be places at first          
            self.quo.procSingleData(index,close_px[index])
            self.mvg.procSingleData(index,close_px[index])
            self.tradesup.setDailyValue(index)
        
        return self.tradesup.getDailyValue()
        
        