'''
calculate simple moving average
'''
import pandas
from collections import OrderedDict

class st_sma:
    def __init__(self):
        self.cleanup()
        self.stname = "st_sma" #strategy name
        
    def cleanup(self):
        self.ind = OrderedDict()
        self.sgy = 1 # default sort all symbols 
        return

    def usage(self):
        return "available parameter:topperf;topperf_is,sort24,sort12,sort4,sort1,help"

    def getIndicators(self):
        return self.ind    

    def setupParam(self,param):
        return
      
    # chart pattern recognize
    # move to standard package
    def cpr(self):
        return
        
    '''
    ma10,ma50,ma200
    '''
    def algoFunc(self, px):
        plen = len(px)        
        if plen >= 10:
            ma10 = pandas.stats.moments.rolling_mean(px,10)
            self.ind['ma10'] = ma10[-1]
        if plen >= 50:
            ma50 = pandas.stats.moments.rolling_mean(px,50)
            self.ind['ma50'] = ma50[-1]
        if plen >= 100:
            ma100 = pandas.stats.moments.rolling_mean(px,100)
            self.ind['ma100'] = ma100[-1]
        if plen >= 200:
            ma200 = pandas.stats.moments.rolling_mean(px,200)
            self.ind['ma200'] = ma200[-1]
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)
     
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        

    def runScan(self,table):
        return table