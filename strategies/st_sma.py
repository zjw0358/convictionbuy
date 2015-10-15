'''
calculate simple moving average
'''
#import pandas
#from collections import OrderedDict
from ind_ma import ind_ma

class st_sma(ind_ma):
    def __init__(self):
        self.cleanup()

        
    def cleanup(self):
        self.offset = 3 #cross in past 3 bars
        self.lookback = 10 #look back 10days
        self.diff = 1 #diff from ma < 1%  
        return

    def usage(self):
        return "px>ma200"

#    def getIndicators(self):
#        return self.ind    

    def setupParam(self,param):
        return
        
#    def needPriceData(self):
#        return True
  
    # chart pattern recognize
    # move to standard package
 #   def cpr(self):
 #       return
        
    '''
    ma10,ma50,ma200
    '''
    def algoFunc(self, px):
        plen = len(px)  
        #print "len=",plen
        self.ma10=[]      
        self.ma50=[]
        self.ma100=[]
        self.ma200=[]
        if plen >= 10:
            ma10 = pandas.stats.moments.rolling_mean(px,10)
            self.ind['ma10'] = round(ma10[-1],2)
        if plen >= 50:
            ma50 = pandas.stats.moments.rolling_mean(px,50)
            self.ind['ma50'] = round(ma50[-1],2)
        if plen >= 100:
            ma100 = pandas.stats.moments.rolling_mean(px,100)
            self.ind['ma100'] = round(ma100[-1],2)
        if plen >= 200:
            ma200 = pandas.stats.moments.rolling_mean(px,200)
            self.ind['ma200'] = round(ma200[-1],2)
           

    def runStrategy(self):
        # price cross above MA 10 
        # MA 50 cross above MA 200
        #self.ind['sma_buy'] = 0
        offset = 50
        prev = self.close_px[-offset]
        for idx, item in enumerate(self.ma10[-offset:]):
            print idx,-offset+idx
            px = self.close_px[-offset+idx]
            if (prev < item) and (px > item) :
                self.ind['sma10_buy'] = "True(%d)" % (offset-idx)
            if (prev > item) and (px < item):                
                self.ind['sma10_sell'] = "True(%d)" % (offset-idx)
            prev = px
        return
        '''
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
            
        pass
    def runScan(self,table):
        return table