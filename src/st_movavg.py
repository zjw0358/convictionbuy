import math
import pandas as pd

class st_movavg:
    def __init__(self,bt):
        self.stname = "movavg" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        self.cleanup()
        
    def cleanup(self):
        self.mapair=[]
        self.madict={}
        self.pcma=0
        
    def setup(self):
        print "========ST_MOVAVG SETUP ========================================"
        for slow,fast in self.mapair:
            print "+ MA pair,slow=",slow,",fast=",fast
        print "================================================================"

    def getStrategyName(self):
        return self.stname
    
    def procSingleData(self,index,price):
        mvBuyFlag = True
        mvSellFlag = True
        for slow,fast in self.mapair:
            slowMvg = self.dfmv[slow].iloc[index]
            fastMvg = self.dfmv[fast].iloc[index]
            if fastMvg<=slowMvg:
                mvBuyFlag=False
            if fastMvg>slowMvg:
                mvSellFlag=False
        
        pcmaBuyFlag=True
        pcmaSellFlag=True
        if self.pcma!=0:
            mvg=self.dfmv[self.pcma].iloc[index]
            if price>mvg:
                pcmaSellFlag=False
            else:
                pcmaBuyFlag=False
                
        if mvBuyFlag and pcmaBuyFlag:
            self.tradesup.buyorder(self.stname)
            #print "mvg buy@",index,price
        elif mvSellFlag and pcmaSellFlag:
            self.tradesup.sellorder(self.stname)
            #print "mvg sell@",index,price        
        return
        
        
    def runStrategy(self,symbol,ohlc):
        self.tradesup.setup(ohlc,10000)
        self.dfmv = pd.DataFrame(index=ohlc.index)
        close_px = ohlc['Adj Close']  
        for mvkey in self.madict:
            if self.madict[mvkey]==1:
                self.dfmv[mvkey] = pd.rolling_mean(close_px, mvkey)
        
        return self.dfmv

    def process(self,bt,symbol,param,ohlc_px,spy_px):        
        #different approach        
        if param['mode']=='1':
            #self.processOptimization(symbol,ohlc_px,spy_px)
            return None
        elif param['mode']==None or param['mode']=='0':            
            #self.setup(win)
            dv = self.runStrategy(ohlc_px)
            print dv
            return dv
        return None

########################################################################
#  optional functions
########################################################################
    def addMApair(self,slow,fast):
        self.mapair.append((slow,fast))
        self.madict[slow]=1        
        self.madict[fast]=1
    
    # set price cross over/below pcma trigger buy/sell signal
    def addPxCrossMa(self,pcma):
        self.pcma=pcma
        self.madict[pcma]=1  
        
