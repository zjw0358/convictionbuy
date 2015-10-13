'''
RSI indicator
'''
from collections import OrderedDict
import numpy as np

class ind_rsi:
    def __init__(self):
        self.cleanup()
        self.stname = "rsi" #strategy name        
    
    def cleanup(self):
        self.ind = OrderedDict()
        return    
    
    def usage(self):
        return "length=14"
    
    def setupParam(self,param):
        # default parameter
        self.cl = 14  
        if 'cl' in param:
            self.cl = int(param['length'])
        
    def algoFunc(self, prices):
        deltas = np.diff(prices)
        seed = deltas[:self.cl+1]
        up = seed[seed>=0].sum()/self.cl
        down = -seed[seed<0].sum()/self.cl
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:self.cl] = 100. - 100./(1.+rs)
    
        for i in range(self.cl, len(prices)):
            delta = deltas[i-1] # cause the diff is 1 shorter
    
            if delta>0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
    
            up = (up*(self.cl-1) + upval)/self.cl
            down = (down*(self.cl-1) + downval)/self.cl
    
            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)
        # get the last one
        self.ind['rsi'] = rsi[-1]
        
    
    #it is price data module(need real price data)
    def needPriceData(self):
        return True
    
    # main process routine, 
    # symbol - stock name
    # ohlc - candle style price,open,high,low,close
    # param - parameters
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)     
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        

    def getIndicators(self):
        return self.ind
        
    # do nothing
    def runScan(self,table): 
        #summary statistics
        print table['rsi'].describe()
        num = float(table['rsi'].count())
        #df = table[table['rsi']>70]['rsi']
        #print df.count()
        overbought = table[table['rsi']>70]['rsi'].count()        
        oversold = table[table['rsi']<30]['rsi'].count()
        strong =  table[table['rsi']>=50]['rsi'].count()
        weak =  table[table['rsi']<50]['rsi'].count()
        print "total numer", num
        print "over bought", overbought/num
        print "over sold", oversold/num
        print "strong", strong/num
        print "weak", weak/num
        return table