'''
MACD
'''
from ind_base_px import BaseIndPx
from pandas import *

class ind_macd(BaseIndPx):
    def algoFunc(self,df):
        n_fast = 12
        n_slow = 26
        #def MACD(df, n_fast, n_slow):
        EMAfast = Series(ewma(df['Close'], span = n_fast, min_periods = n_slow - 1))
        EMAslow = Series(ewma(df['Close'], span = n_slow, min_periods = n_slow - 1))
        MACD = Series(EMAfast - EMAslow, name = 'MACD_' + str(n_fast) + '_' + str(n_slow))
        MACDsign = Series(ewma(MACD, span = 9, min_periods = 8), name = 'MACDsign_' + str(n_fast) + '_' + str(n_slow))
        MACDdiff = Series(MACD - MACDsign, name = 'MACDdiff_' + str(n_fast) + '_' + str(n_slow))
        df = df.join(MACD)
        df = df.join(MACDsign)
        df = df.join(MACDdiff)
        print df
        self.ind['macd'] = MACD[-1]
        self.macd = MACD
        return df
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #self.setupParam(param)     
        #self.close_px = ohlc['Adj Close']
        self.algoFunc(ohlc)  