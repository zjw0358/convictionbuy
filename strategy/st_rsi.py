import numpy as np

class st_rsi:
    def __init__(self,bt):
        self.cleanup()
        self.stname = "rsi" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
    def getStrategyName(self):
        return self.stname
    
    # called this when doing automation test
    def cleanup(self):
        self.rsi = []
        return
        
    def getSetupInfoStr(self):
        return self.setupInfo
        
    def setup(self,cl):
        self.cleanup() #must call cleanup before test
        self.cl = cl  
        self.setupInfo = "cutoff length=%d" % self.cl 
        #self.setupInfo = \
        #"=== ST_RSI SETUP===========================================\n" + \
        #"cutoff length=%d\n" % self.cl + \
        #"===========================================================\n"
        #print self.setupInfo

    def setupParam(self,param):
        # default parameter
        cl = 14
        if 'cl' in param:
            cl = int(param['cl'])
        self.setup(cl)

    def rsiFunc(self, prices):
        deltas = np.diff(prices)
        seed = deltas[:self.cl+1]
        up = seed[seed>=0].sum()/self.cl
        down = -seed[seed<0].sum()/self.cl
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:self.cl] = 100. - 100./(1.+rs)
    
        for i in range(self.cl, len(prices)):
            delta = deltas[i-1] # cause the diff is 1 shorter
    
            if delta>0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
    
            up = (up*(self.cl-1) + upval)/self.cl
            down = (down*(self.cl-1) + downval)/self.cl
    
            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)    
        return rsi
        
    def getIndicatorVal(self):
        indStr = "%.2f,%.2f,%.2f" % (self.rsi[-15],self.rsi[-8],self.rsi[-1])
        return indStr

    # strategy, find the buy&sell signal
    def runStrategy(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)

        #self.tradesup.beginTrade(self.setupInfo, symbol, ohlc) 
        #print self.tradesup.getTradeReport()
                
        close_px = ohlc['Adj Close']
        self.rsi = self.rsiFunc(close_px)        
        # loop checking close price
        for index in range(0, len(close_px)):
            self.tradesup.processData(index)  # must be places at first          
            self.procSingleData(index,close_px[index]) # the algorithm
            self.tradesup.calcDailyValue(index) # update daily value
            

        #call this to end trade 
        #self.tradesup.endTrade(self.setupInfo)
        
        #print self.tradesup.getTradeReport()
        #paramstr = "cl=%d"%(self.cl)
        #d0 = self.simutable.procStrategyResult(self.setupInfo, paramstr,self.tradesup.getDailyValue(), self.getMoreInfo())
        #d0['val'] = round(self.rsi[-1],2)
        #return d0
        
    def runOptimization(self,symbol,ohlc,bm):
        tset = range(10, 30, 1)

        
        #must setup report tool before simulation test
        #self.simutable.setupSymbol(symbol,bm)

        for t in tset:        
            self.setup(t)
            self.runStrategy(symbol,ohlc)
            # to generate simulation report
            #param = "cl=%d"%(t)
            #self.simutable.addOneTestResult(self.setupInfo, param,self.tradesup.getDailyValue(), self.getMoreInfo())
        
        #add results to report
        #self.simutable.makeSimuReport()
        #self.tradesup.setDailyValueDf(self.simutable.getBestDv())
        return
        
    def getMoreInfo(self):
        #last rsi readout 
        info = "rsi=%.2f" %(self.rsi[-1])        
        return info
    
    # process single date data        
    def procSingleData(self, index, ohlc):
        # trading signal
        if (self.rsi[index] < 30):          
            self.tradesup.buyorder(self.stname)
            #print "rsi buy@",index,self.rsi[index]
                
        if (self.rsi[index] > 70):
            self.tradesup.sellorder(self.stname)
            #print "rsi sell@",index,self.rsi[index]
        return
