import numpy as np
'''
an expert of a system
technical analysis of stock and commodity 
2013 oct
'''
class st_aeoas:
    def __init__(self, bt):
        self.cleanup()
        self.stname = "aeoas" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        
    def setupParam(self,param):
        # default parameter
        typWin = 5
        hacWin = 8

        if 't' in param:
            typWin = float(param['t'])
        if 'h' in param:
            hacWin = float(param['h'])
            
        self.setup(typWin, hacWin)
           
    def setup(self, typWin, hacWin):
        self.cleanup()
        self.typema1 = 2.0/(typWin+1)
        self.typema2 = 1 - self.typema1
        self.hacema1 = 2.0/(hacWin+1)
        self.hacema2 = 1 - self.hacema1
        self.typWin = typWin
        self.hacWin = hacWin
        print "=== A EXPERT OF A SYSTEM SETUP==========================================="
        print "typical period=",typWin,self.typema1,self.typema2
        print "heikin-ashi period=",hacWin,self.hacema1,self.hacema2
        print "================================================================"
        return
        
    def getStrategyName(self):
        return self.stname
        
    # called this when doing automation test
    def cleanup(self):
        self.haopenLst=[]
        self.haCLst=[]
        self.typicalLst=[]
        self.avgTypEmaLst=[]
        self.avgHacEmaLst=[]
        return
    
    ############################################################################
    # ALGORITHM
    ############################################################################    
    
    # process single date data        
    def procSingleData(self, index, ohlc):
        avg0 = (ohlc['High'] + ohlc['Low'] + ohlc['Close'] + ohlc['Open'])/4
        avg1 = (self.ohlc['High'].iloc[index-1] + self.ohlc['Low'].iloc[index-1] + self.ohlc['Close'].iloc[index-1] + self.ohlc['Open'].iloc[index-1])/4
        typical = (ohlc['High'] + ohlc['Low'] + ohlc['Close']) / 3

        if index > 0:
            haOpen = (avg1 + self.haopenLst[index-1])/2
            avgTyp = typical*self.typema1 + self.typema2*self.avgTypEmaLst[index-1]
        else:
            haOpen = 0
            avgTyp = typical
        haC = (avg0 + haOpen + max(ohlc['High'],haOpen) + min(ohlc['Low'], haOpen)) / 4
        
        if index > 0:
            avgHac = haC*self.hacema1 + self.hacema2*self.avgHacEmaLst[index-1]
        else:
            avgHac = haC

        self.haCLst.append(haC)
        self.haopenLst.append(haOpen)
        self.typicalLst.append(typical)
        self.avgTypEmaLst.append(avgTyp)
        self.avgHacEmaLst.append(avgHac)
        
        # trading signal
        if (avgTyp > avgHac) and (ohlc['Close'] > ohlc['Open']):          
            self.tradesup.buyorder(self.stname)
            #print "aeoas buy@",index
                
        if (avgTyp < avgHac) and (ohlc['Close'] < ohlc['Open']):
            self.tradesup.sellorder(self.stname)
            #print "aeoas sell@",index,avgTyp,avgHac,ohlc['Close'],ohlc['Open']
        return 
       
  

    def moving_average(self,x, n, type='simple'):
        """
        compute an n period moving average.    
        type is 'simple' | 'exponential'    
        """
        x = np.asarray(x)
        if type=='simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))
    
        weights /= weights.sum()
        
        a =  np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]        
        return a
    

    def runStrategy(self,symbol,ohlc):
        #initialize tradesupport
        self.tradesup.setup(symbol, ohlc) 
        self.ohlc = ohlc
        #self.tradesup.setStopLimit(1)
        #self.tradesup.setStopLoss(2)
        # loop checking close price
        for index in range(0, len(ohlc)):
            self.tradesup.processData(index)  # must be places at first          
            self.procSingleData(index,ohlc.iloc[index]) # the algorithm
            self.tradesup.calcDailyValue(index) # update daily value
            
        #call this to create daily value data frame
        self.tradesup.createDailyValueDf()
        
        #paramstr = "t=%d&h=%d"%(self.typWin,self.hacWin)
        #self.simutable.addOneTestResult(paramstr,self.tradesup.getDailyValue())


    def processOptimization(self,symbol,ohlc,bm):
        tset = range(4, 10, 1)
        hset = range(6, 16, 1)
        
        #must setup report tool before simulation test
        self.simutable.setupSymbol(symbol,bm)

        for t in tset:
            for h in hset:
                if t >= h:
                    continue
                self.setup(t, h)
                self.runStrategy(symbol,ohlc)
                # to generate simulation report
                param = "t=%d&h=%d"%(t, h)
                self.simutable.addOneTestResult(param,self.tradesup.getDailyValue(), self.getTypnHac())
        
        #add results to report
        self.simutable.makeSimuReport()
        self.tradesup.setDailyValueDf(self.simutable.getBestDv())
        return
                    
    def getTypnHac(self):
        info = "avgTyp=%.2f,avgHac=%.2f" %(self.avgTypEmaLst[-1], self.avgHacEmaLst[-1])        
        return info
        
    def process(self,bt,symbol,param,ohlc_px,spy_px):
        #different approach
        if param['mode']=='1':
            self.processOptimization(symbol,ohlc_px,spy_px)
            return True
        elif param['mode']==None or param['mode']=='0':            
            self.setupParam(param)
            self.runStrategy(symbol, ohlc_px)
            return True
        return False