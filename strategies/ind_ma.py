'''
calculate simple moving average
'''
import pandas
from collections import OrderedDict
from ind_base_px import BaseIndPx

class ind_ma(BaseIndPx):
    #def __init__(self):
    #    self.cleanup()
    #    self.stname = "ind_sma" #strategy name
        
    #def cleanup(self):
    #    self.ind = OrderedDict()
        #self.offset = 3 #cross in past 3 bars
        #self.lookback = 10 #look back 10days
        #self.diff = 1 #diff from ma < 1%  
    #    return

    def usage(self):
        return "ma=length"

    #def getIndicators(self):
    #    return self.ind    

    def setupParam(self,param):
        return
        
#    def needPriceData(self):
#        return True
  
    # chart pattern recognize
    # move to standard package
    #def cpr(self):
    #    return
        
    '''
    ma10,ma50,ma200
    '''
    def algoFunc(self, px):
        plen = len(px)  
        #print "len=",plen
        self.ma10 = []
        self.ma50 = []
        self.ma100 = []
        self.ma200 = []
        # pandas.core.series.Series()
        if plen >= 10:
            self.ma10 = pandas.stats.moments.rolling_mean(px,10).tolist()
            self.ind['ma10'] = round(self.ma10[-1],2)
        if plen >= 50:
            self.ma50 = pandas.stats.moments.rolling_mean(px,50).tolist()
            self.ind['ma50'] = round(self.ma50[-1],2)
        if plen >= 100:
            self.ma100 = pandas.stats.moments.rolling_mean(px,100).tolist()
            self.ind['ma100'] = round(self.ma100[-1],2)
        if plen >= 200:
            self.ma200 = pandas.stats.moments.rolling_mean(px,200).tolist()
            self.ind['ma200'] = round(self.ma200[-1],2)
            ''' TODO
            self.ind['px_cross_sma_buy'] = 0
            count = 0
            for index in range(1,plen+1):
                if px[-index] > ma200[-index]:
                    buy = True
                    for prev in range(index+1,index+11):
                        if px[-prev] > ma200[-prev]:
                            buy = False
                            break;
                    if buy==True:
                        self.ind['px_cross_sma_buy'] = 1
                    break
                count+=1
                if count>=self.offset:
                    break;
            '''
    #it is price data module(need real price data)
#    def needPriceData(self):        
#        return True

#    def getIndicators(self):
#        return self.ind


    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)     
        self.close_px = ohlc['Adj Close']
        self.algoFunc(self.close_px)        

    def runScan(self,table):
        return table