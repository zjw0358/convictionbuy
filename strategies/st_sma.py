'''
simple moving average strategy
'''

from ind_ma import ind_ma
from st_pattern import StrategyPattern
from trade_support import TradeSupport

class st_sma(ind_ma):
    def usage(self):
        return "px>ma200"
   
    def runIndicator(self,symbol,ohlc,param={}):
        ind_ma.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
    
    def algoStrategy(self, ohlc):
        # price cross above MA10 and crosee below MA10
        sp = StrategyPattern()
        tsup = TradeSupport()
        px = ohlc['Adj Close']
        if (self.ma10):
            buysg,sellsg = sp.divergencyCross(px, self.ma10, 2)
            tsup.getLastSignal(buysg,sellsg,self.ind,'ma10_buy','ma10_sell')
        
        if (self.ma50):
            buysg,sellsg = sp.divergencyCross(px, self.ma50, 2)
            tsup.getLastSignal(buysg,sellsg, self.ind,'ma50_buy','ma50_sell')            
                
        #too lag, how about px cross MA50        
        if (self.ma50 and self.ma200):
            #print "test golder and death"
            buysg,sellsg = sp.cross(self.ma50, self.ma200, 2)
            #print sellsg
            tsup.getLastSignal(buysg,sellsg, self.ind,'ma50_200_buy','ma50_200_sell')          
        pass

