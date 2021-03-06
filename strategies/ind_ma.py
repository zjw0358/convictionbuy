'''
calculate simple moving average
'''

import pandas
from ind_base_px import BaseIndPx

class ind_ma(BaseIndPx):
    def usage(self):
        return "ma=length"

        
    '''
    ma10,ma50,ma200
    '''
    def algoFunc(self, df):
        plen = len(df)  
        #px = df['Adj Close']
        px = df['Close']
        
        # pandas.core.series.Series()
        if plen >= 10:
            self.ma10 = pandas.stats.moments.rolling_mean(px,10).tolist()
            self.ind['ma10'] = round(self.ma10[-1],2)
            #df['ma10']=self.ma10
        if plen >= 50:
            self.ma50 = pandas.stats.moments.rolling_mean(px,50).tolist()
            self.ind['ma50'] = round(self.ma50[-1],2)
            #df['ma50'] = self.ma50
        if plen >= 100:
            #self.ma100 = pandas.stats.moments.rolling_mean(px,100)#.tolist()
            self.ma100 = pandas.rolling_mean(px,100).tolist()
            self.ind['ma100'] = round(self.ma100[-1],2)
        if plen >= 200:
            #self.ma200 = pandas.stats.moments.rolling_mean(px,200).tolist()
            self.ma200 = pandas.rolling_mean(px,200)
            self.ind['ma200'] = round(self.ma200[-1],2)
            #df['ma200'] = self.ma200           
        #print df
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)     
        #self.close_px = ohlc['Adj Close']
        self.algoFunc(ohlc)
