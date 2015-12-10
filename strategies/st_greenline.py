'''
above green line
'''

from ind_base_px import BaseIndPx
from ind_sctr import ind_sctr
from ind_kdj import ind_kdj
from ind_cbbase import *
from ind_dmi import ind_dmi
from st_pattern import StrategyPattern
from trade_support import TradeSupport

class st_greenline(BaseIndPx):
    def __init__(self): 
        BaseIndPx.__init__(self)    
        self.ind_sctr = ind_sctr()
        self.ind_kdj = ind_kdj()
        self.ind_dmi = ind_dmi()
        self.sp = StrategyPattern()
        self.tsup = TradeSupport()
        pass
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):  
        '''
        my STO implementation is more promise
        '''
        self.setupParam(param) #parent func      
        self.ind_sctr.runIndicator(symbol,ohlc,param)
        self.ind['sctr'] = self.ind_sctr.ind['sctr']
        self.ind_kdj.runIndicator(symbol,ohlc,param)
        self.ind['money_wave'] = self.ind_kdj.ind['slow_d']        
        
        buysg,sellsg = self.sp.crossValue(self.ind_sctr.score, self.ind_sctr.score,0,0,2)
        self.tsup.getLastSignal(buysg,sellsg, self.ind,'sctr_buy','sctr_sell')

        #self.ind_dmi.runIndicator(symbol,ohlc,param)
        #print self.ind_kdj.
        #df = STO(ohlc,5)
        #df = ADX(ohlc,14,14)
        #print df
        #self.algoStrategy(ohlc)
        pass
        
    def runScan(self,df):
        if not self.param:
            return df
        total = len(df)
        df['sctrrank'] = df['sctr'].rank(ascending=1)/total*100
        df.sort_index(by="sctrrank",inplace=True,ascending=False)
        col = df.columns.values 
        df = self.mtd.evalCriteria(df,self.param,col) 
        return df 