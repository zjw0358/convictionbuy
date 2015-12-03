'''
%K = 100 * (Close-LowestLow[last n periods])/(HighestHigh[last n periods]-LowestLow[last n periods])

%D = MovingAverage(%K)
'''
import pandas as pd
from ind_base_px import BaseIndPx

class ind_kdj(BaseIndPx):
    def usage(self):
        return "length=[14]"
    #override func
    def setupParam(self,param):
        BaseIndPx.setupParam(self,param)  
        self.cl = 14  
        if 'cl' in param:
            self.cl = int(param['length'])
    def algoFunc(self, px):
        l = pd.rolling_min(px['Low'], self.cl) 
        h = pd.rolling_max(px['High'], self.cl)
        k = 100 * (px['Close'] - l) / (h-l)
        d = pd.rolling_mean(k, 3)
        slowk = d
        slowd = pd.rolling_mean(slowk, 3)
        j = 3 * d - 2 * k
        #px['j'] = j
        '''
        px['fast_k'] = k
        px['fast_d'] = d        
        px['slow_d'] = slowd
        '''        
        #print px
        self.ind['slow_d'] = slowd[-1]
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)
        self.algoFunc(ohlc)     
        