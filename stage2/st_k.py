from marketscan import *
from ind_base_px import BaseIndPx
from st_pattern import StrategyPattern
from trade_support import TradeSupport

'''

'''
class st_k(BaseIndPx):
    def __init__(self):
        self.sp = StrategyPattern()
        self.tsup = TradeSupport()

    def setupParam(self, param):
        pass

    def _algo(self, ohlc):
        pass

    def runIndicator(self, symbol, ohlc, param={}):
        ind_ma = importStrategy("ind_ma", symbol, ohlc)

        #s1 = ind_ma.ma50
        s1 = pandas.rolling_mean(ind_ma.ma50, 3) #.tolist()
        s2 = s1.shift(2)
        delta = s1 - s2
        #ohlc['delta'] = delta
        # ohlc
        buysg, sellsg = self.sp.crossValue(delta, delta, 0, 0, 1)
        ohlc['ag50b'] = buysg
        ohlc['ag50s'] = sellsg
        self.tsup.getLastSignal(buysg, sellsg, self.ind, 'ag50b','ag50s')

        s1 = pandas.rolling_mean(ind_ma.ma10, 3) #.tolist()
        s2 = s1.shift(2)
        delta = s1 - s2
        #ohlc['delta'] = delta
        # ohlc
        buysg, sellsg = self.sp.crossValue(delta, delta, 0, 0, 2)
        ohlc['ag10b'] = buysg
        ohlc['ag10s'] = sellsg

        # get all signal idx
        ag10bidx, ag10sidx = self.tsup.getLastSignal(buysg, sellsg, self.ind, 'ag10b', 'ag10s')
        vol10bidx = ind_ma.ind['vol10b']
        ma10bidx = ind_ma.ind['ma10b']

        pass