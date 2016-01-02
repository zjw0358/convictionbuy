from ind_macd import ind_macd
from st_pattern import StrategyPattern
from trade_support import TradeSupport

class st_macd(ind_macd):
    def __init__(self):
         # price cross above MA10 and crosee below MA10
        self.sp = StrategyPattern()
        self.tsup = TradeSupport()
    def runIndicator(self,symbol,ohlc,param={}):
        if 'nbar' in param:
            self.nbar = int(param['nbar'])
        else:
            self.nbar = 1
            
        ind_macd.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
        
    def algoStrategy(self, ohlc):
        sp = self.sp
        tsup = self.tsup
        #print self.macd
        buysg,sellsg = sp.crossValue(self.macd, self.macd, 0, 0, self.nbar)
        #print buysg
        tsup.getLastSignal(buysg,sellsg,self.ind,'macdb','macds')
        