import pandas as pd
import st_quotient
import st_movavg
import st_erdate

class stc_quomv:
    def __init__(self,bt):
        self.stname = "comb_quomv" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        #this strategy is consist of several strateges
        self.quo = st_quotient.st_quotient(bt)
        self.mvg = st_movavg.st_movavg(bt)
        self.erd = st_erdate.st_erdate(bt)
  
    def getStrategyName(self):
        return self.stname
              
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
        erdwin=1
        
        if 'erdwin' in param:
            erdwin = int(param['erdwin'])
            
        #setup component
        self.tradesup.addStrategy(self.quo.getStrategyName())
        #self.tradesup.addStrategy(self.mvg.getStrategyName())
        #self.tradesup.addStrategy(self.erd.getStrategyName())
        


        #different approach        
        if param['mode']=='1':
            #self.processOptimization(symbol,ohlc_px,spy_px)
            return False
        elif param['mode']==None or param['mode']=='0':            
            #self.mvg.cleanup()
            #self.erd.setup(erdwin)
            self.quo.setup(k1,k2,cl)
            #self.mvg.addMApair(200,50)            
            #self.mvg.addPxCrossMa(200)
            #self.mvg.setup()
            self.runStrategy(symbol,ohlc_px)            
            return True
        return False
        
    def runStrategy(self,symbol,ohlc):
        self.tradesup.setup(ohlc,10000)
        close_px = ohlc['Adj Close']  
        #self.mvg.runStrategy(symbol,ohlc)
        #self.erd.runStrategy(symbol,ohlc)

        for index in range(0, len(close_px)):
            #since this is combo strategy, the combo itself always give 'buy' order
            self.tradesup.buyorder(self.stname)
            
            self.tradesup.processData(index)  #must be places at first          
            self.quo.procSingleData(index,close_px[index])
            #self.mvg.procSingleData(index,close_px[index])
            #self.erd.procSingleData(index,close_px[index])
            self.tradesup.setDailyValue(index)
            #print self.tradesup.stgyorder
        return True
        #return self.tradesup.getDailyValue()
        
        