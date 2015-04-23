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
        self.offset = 3 #cross in past 3 bars
        self.lookback = 10 #look back 10days
        self.diff = 1 #diff from ma < 1%  
        return

    def usage(self):
        return "px>ma200"

    def getIndicators(self):
        return self.ind    

    def setupParam(self,param):
        return
        
    def needPriceData(self):
        return True
  
    # chart pattern recognize
    # move to standard package
    def cpr(self):
        return
        
    '''
    ma10,ma50,ma200
    '''
    def algoFunc(self, px):
        plen = len(px)  
        #print "len=",plen
        ma10=[]      
        ma50=[]
        ma100=[]
        ma200=[]
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

    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)
     
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        

    def runScan(self,table):
        return table