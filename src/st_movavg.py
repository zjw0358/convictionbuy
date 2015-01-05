import math
import pandas as pd

class st_movavg:
    #for optimization test        
    def setup(self,win):
        self.win = win        
        print "========ST_MOVAVG SETUP ========================================"
        print "window",self.win
        print "================================================================"
        
    def process(self,bt,symbol,param,ohlc_px,spy_px):
        # parameter
        win = 200
        
        if 'win' in param:
            win = float(param['win'])
        
        #setup component
        self.support = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        
        #different approach        
        if param['mode']=='1':
            #self.processOptimization(symbol,ohlc_px,spy_px)
            return None
        elif param['mode']==None or param['mode']=='0':            
            self.setup(win)
            dv = self.processAllPriceData(ohlc_px)
            print dv
            return dv
        return None
        
    def processAllPriceData(self,ohlc):
        self.support.setup(ohlc,10000)
        close_px = ohlc['Adj Close']  
        ohlc['dayvalue'] = pd.rolling_mean(close_px, self.win)
        return ohlc
        