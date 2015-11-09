#import numpy as np
'''
an expert of a system
technical analysis of stock and commodity 
2013 oct

TODO improve :need 2 days observe window?
'''

from st_pattern import StrategyPattern
from trade_support import TradeSupport
from ind_aeoas import ind_aeoas


class st_aeoas(ind_aeoas):
    def runIndicator(self,symbol,ohlc,param={}):
        ind_aeoas.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
      
    '''
        # trading signal
        if (avgTyp > avgHac) and (ohlc['Close'] > ohlc['Open']):          
            self.tradesup.buyorder(self.stname)
            #print "aeoas buy@",index
                
        if (avgTyp < avgHac) and (ohlc['Close'] < ohlc['Open']):
            self.tradesup.sellorder(self.stname)
            #print "aeoas sell@",index,avgTyp,avgHac,ohlc['Close'],ohlc['Open']
        return 
    '''
    def algoStrategy(self, ohlc):
        # price cross above MA10 and crosee below MA10
        sp = StrategyPattern()
        tsup = TradeSupport()

        buysg1,sellsg1 = sp.compare(self.avgTypEmaLst, self.avgHacEmaLst, self.hacWin*2)        
        buysg2,sellsg2 = sp.compare(ohlc['Close'], ohlc['Open'], self.hacWin*2)
        buysg = sp.combineAndSignal(buysg1,buysg2)
        sellsg = sp.combineAndSignal(sellsg1,sellsg2)
        signal = map(sp.mergeSignal, buysg,sellsg,[])
                
        ohlc['signal'] = signal
        ohlc['buy1'] = buysg1
        ohlc['buy2'] = buysg2
        ohlc['buy3'] = buysg
        ohlc['sell1'] = sellsg1
        ohlc['sell2'] = sellsg2
        ohlc['sell3'] = sellsg

        print ohlc
        
        #tsup.getLastSignal(buysg,sellsg,self.ind,'ma10_buy','ma10_sell')
        

        #too lag, how about px cross MA50
        '''
        if (self.ma50 and self.ma200):
            sp.initData(self.ma50, self.ma200, 200)
            self.ind['ma50_200_buy'] = sp.crossAbove()
            self.ind['ma50_200_sell'] = sp.crossBelow()
        '''    
        pass
               

    
    
    