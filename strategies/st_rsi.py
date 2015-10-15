'''
strategy based on RSI indicator
'''
from ind_rsi import ind_rsi

class st_rsi(ind_rsi):
    def __init__(self):
        pass
        
    # main process routine, 
    # symbol - stock name
    # ohlc - candle style price,open,high,low,close
    # param - parameters
    #def runIndicator(self,symbol,ohlc,param={}):
        #work for new style class only
        #super(st_rsi,self).runIndicator(symbol,ohlc,param)
    #    ind_rsi.runIndicator(self,symbol,ohlc,param)
        
    def runStrategy(self):
        #print "I am in st_rsi runstrategy"
        #print self.rsi
        offset = 14
        OVERSELL = 30
        OVERBUY = 70
        prev = self.rsi[-offset]
        for idx, rs in enumerate(self.rsi[-offset:]):            
            if (prev < OVERSELL) and (rs > OVERSELL) :
                self.ind['rsi_buy'] = "True(%d)" % (offset-idx)
            if (prev > OVERBUY) and (rs < OVERBUY):                
                self.ind['rsi_sell'] = "True(%d)" % (offset-idx)
            prev = rs
        return
        
    #def getIndicators(self):
    #    return self.ind

#===============================================================================        
    # RSI strategy
    def runScan(self,table): 
        #summary statistics
        if 'rsi' in table:
            print table['rsi'].describe()
            num = float(table['rsi'].count())
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