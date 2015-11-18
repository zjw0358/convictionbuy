'''
RSI indicator
'''
#from collections import OrderedDict
from ind_base_px import BaseIndPx
import numpy as np

class ind_rsi(BaseIndPx):
    def usage(self):
        return "length=14"
    
    #override func
    def setupParam(self,param):
        BaseIndPx.setupParam(self,param)  
        self.cl = 14  
        if 'cl' in param:
            self.cl = int(param['length'])
            
        
    def algoFunc(self, prices):
        deltas = np.diff(prices)
        seed = deltas[:self.cl+1]
        up = seed[seed>=0].sum()/self.cl
        down = -seed[seed<0].sum()/self.cl
        rs = up/down
        self.rsi = np.zeros_like(prices)
        self.rsi[:self.cl] = 100. - 100./(1.+rs)
    
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
            self.rsi[i] = 100. - 100./(1.+rs)
        # get the last one
        self.ind['rsi'] = self.rsi[-1]
        
        
    # main process routine, 
    # symbol - stock name
    # ohlc - candle style price,open,high,low,close
    # param - parameters
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)     
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        

#===============================================================================        
    # RSI strategy
    '''
    def runScan(self,table): 
        #summary statistics
        if 'rsi' in table:
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
    ''' 
    '''            
    def runStrategy(self):
        offset = 14
        OVERSELL = 30
        OVERBUY = 70
        prev = self.rsi[-offset]
        #print self.rsi
        #print "==============================="
        for idx, rs in enumerate(self.rsi[-offset:]):            
            if (prev < OVERSELL) and (rs > OVERSELL) :
                self.ind['rsi_buy'] = "True(%d)" % (offset-idx)
            if (prev > OVERBUY) and (rs < OVERBUY):                
                self.ind['rsi_sell'] = "True(%d)" % (offset-idx)
            prev = rs
        return
    '''  
    '''
    def __init__(self):
        self.cleanup()
        self.stname = "rsi" #strategy name            

    def cleanup(self):
        self.ind = OrderedDict()
        self.rsi = []
        return    
    ''' 