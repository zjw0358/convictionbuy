from marketscan import *
from ind_base_px import BaseIndPx

class st_k(BaseIndPx):
    def setupParam(self, param):
        pass

    def runIndicator(self, symbol, ohlc, param={}):
        ind_ma = importStrategy("ind_ma", symbol, ohlc)
        print ind_ma.ma10
        pass