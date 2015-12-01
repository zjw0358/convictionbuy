from ind_base_px import BaseIndPx
import math
import numpy as np
import pandas
import ind_cbbase

def calcDX(pdi,ndi):
    pdi = max(pdi,0)
    ndi = max(ndi,0)
    return 100 * abs(pdi-ndi)/(pdi+ndi)
    '''
    if (pdi+ndi > 0):
        return 100 * abs(pdi-ndi)/(pdi-ndi)
    else:
        return 0
    '''
        
class ind_dx(BaseIndPx):
    def usage(self):
        return "trendline"
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #print ohlc
        self.setupParam(param)
        self.algoFunc(ohlc)        

    def algoFunc(self,df):
        #df0.apply(math.log,df0['Adj Close'])
        #df['log_ret'] = np.log(df['Adj Close'])-(np.log(df['Adj Close'].shift(1)))
        df['log'] = np.log(df['Adj Close'])
        df['dxp'] = df['log']-df['log'].shift(1)
        df['dxm'] = (df['log'].shift(1)-df['log'])
        #dx = map(calcDX, df['dxp'].tolist(),df['dxm'].tolist())
        dx = map(calcDX, df['dxp'],df['dxm'])
        print dx
        #df['mean'] = pandas.rolling_sum(df['log_ret'],5)
        #print df['log_ret'].sum()
        #print df
        #print df['mean'].sum()
        pass