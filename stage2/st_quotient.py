# -*- coding: utf-8 -*-
'''
TODO fomurla
quotient strategy
'''

from st_pattern import StrategyPattern
from ind_quotient import ind_quotient
from trade_support import TradeSupport

class st_quotient(ind_quotient):
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):        
        ind_quotient.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
        
    '''
    TODO probably there is a false signal,e.g crossbelow happen after buy signal,should we discard the buy signal?
    '''
    def algoStrategy(self,ohlc):
        sp = StrategyPattern()
        tsup = TradeSupport()
        buysg,sellsg = sp.crossValue(self.quolst, self.shortquolst, 0, 0, 2)        
        
        #process these signale for backtest
        signal = map(sp.mergeSignal, buysg, sellsg, "")
        ohlc['signal'] = signal
        
        
        if (self.debug):
            ohlc['buysignal'] = buysg
            ohlc['sellsignal'] = sellsg
            ohlc['fast'] = self.quolst
            ohlc['slow'] = self.shortquolst
            print ohlc
        

        tsup.getLastSignal(buysg,sellsg, self.ind,'quo_buy','quo_sell')
        pass
