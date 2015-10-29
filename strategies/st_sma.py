'''
simple moving average strategy
'''

from ind_ma import ind_ma
from st_pattern import StrategyPattern
from trade_support import TradeSupport

class st_sma(ind_ma):
    def usage(self):
        return "px>ma200"


    def setupParam(self,param):
        return
        
   
    def runIndicator(self,symbol,ohlc,param={}):
        ind_ma.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
    
    def algoStrategy(self, ohlc):
        # price cross above MA10 and crosee below MA10
        sp = StrategyPattern()
        tsup = TradeSupport()
        if (self.ma10):
            buysg,sellsg = sp.divergencyCross(self.close_px, self.ma10, 2)
            idx,sig = tsup.getLastSignal(buysg,sellsg)
            sigstr = "%d" % (idx)
            if (sig=="buy"):            
                self.ind['ma10_buy'] = sigstr
            else:
                self.ind['ma10_sell'] = sigstr
            
            #ohlc['buy'] = buysg
            #ohlc['sell'] = sellsg
        
        if (self.ma50):
            buysg,sellsg = sp.divergencyCross(self.close_px, self.ma50, 2)
            idx,sig = tsup.getLastSignal(buysg,sellsg)
            sigstr = "%d" % (idx)
            if (sig=="buy"):            
                self.ind['ma50_buy'] = sigstr
            else:
                self.ind['ma50_sell'] = sigstr
                
        #too lag, how about px cross MA50
        '''
        if (self.ma50 and self.ma200):
            sp.initData(self.ma50, self.ma200, 200)
            self.ind['ma50_200_buy'] = sp.crossAbove()
            self.ind['ma50_200_sell'] = sp.crossBelow()
        '''    
        pass
    def runScan(self,table):
        return table

