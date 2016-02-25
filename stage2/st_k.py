from marketscan import *
from ind_base_px import BaseIndPx
from st_pattern import StrategyPattern

class st_k(BaseIndPx):
    def setupParam(self, param):
        pass

    def _algo(self, ohlc):

        pass

    def runIndicator(self, symbol, ohlc, param={}):
        ind_ma = importStrategy("ind_ma", symbol, ohlc)
        sp = StrategyPattern()
        #s1 = ind_ma.ma50
        s1 = pandas.rolling_mean(ind_ma.ma50, 3) #.tolist()
        s2 = s1.shift(2)
        delta = s1 - s2
        ohlc['delta'] = delta
        print ohlc
        buysg,sellsg = sp.crossValue(delta, delta, 0, 0, 2)
        self.tsup.getLastSignal(buysg,sellsg, self.ind,'sctr_buy','sctr_sell')
        #print ind_ma.ma50
        pass