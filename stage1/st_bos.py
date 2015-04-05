#import numpy as np
import datetime
import pandas

'''
param:st_bos&ckd=2015-03-12&r0=1&rc=1&rtd=1&rd=1
'''
class st_bos:
    def __init__(self,bt):
        self.cleanup()
        self.stname = "bos" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        
    def getStrategyName(self):
        return self.stname
    
    # called this when doing automation test
    def cleanup(self):
        self.ind = {}
        self.chkdate = ""
        self.crtd = 1
        self.cr0 = 1
        self.crc = 1
        self.crd = 1
        return
        
    def getSetupInfoStr(self):
        return self.setupInfo
        
    def setup(self,ckd,rtd,r0,rc,rd):
        self.cleanup() #must call cleanup before test
        self.chkdate = ckd
        self.crtd = rtd
        self.cr0 = r0
        self.crc = rc
        self.crd = rd     
        self.setupInfo = "check date=%s,rtd=%d,r0=%d,rd=%d,rc=%d" % \
            (self.chkdate,self.crtd,self.cr0,self.crd,self.crc)

    def setupParam(self,param):
        # default parameter
        chkdate = ""
        rtd = 1
        r0 = 1
        rc = 1
        rd = 1
        if 'ckd' in param:
            chkdate = param['ckd']
        if 'rtd' in param:
            rtd = int(param['rtd'])
        if 'r0' in param:
            r0 = int(param['r0'])
        if 'rc' in param:
            rc = int(param['rc'])
        if 'rd' in param:
            rd = int(param['rd'])
            
        self.setup(chkdate,rtd,r0,rc,rd)

    def algoFunc(self, prices):
        rtd = (prices[-1]/prices[0] - 1)*100
        self.ind['BOS_RTD'] = rtd
        if self.chkdate:
            ckdidx = prices.index.get_loc(self.chkdate)
            ex_ckdidx = ckdidx - 1
            #print "ex chk date",ex_ckdidx
            self.ind['BOS_R0'] = (prices[ex_ckdidx]/prices[0] - 1)*100
            self.ind['BOS_RC'] = (prices[-1]/prices[ckdidx] - 1)*100
            self.ind['BOS_RD'] = self.ind['BOS_RTD'] - self.ind['BOS_R0'] - self.ind['BOS_RC']
        else:
            print "Warning: No check date, only calculate return to date"
            
    def getIndicators(self):
        return self.ind

    # strategy, find the buy&sell signal
    def runStrategy(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)

        #self.tradesup.beginTrade(self.setupInfo, symbol, ohlc) 
        #print self.tradesup.getTradeReport()
                
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        
        
        # loop checking close price
        '''
        for index in range(0, len(close_px)):
            self.tradesup.processData(index)  # must be places at first          
            self.procSingleData(index,close_px[index]) # the algorithm
            self.tradesup.calcDailyValue(index) # update daily value
        '''
         

  

    def filterOut(self,table,benchStr):
        if not self.chkdate:
            print "No filting was done because there is no check date, return"
            return pandas.DataFrame(columns=table.columns) 
        df = table.loc[table['symbol'] == benchStr]
        print df
        
        bmrtd = df.loc[0,'BOS_RTD']
        bmr0 = df.loc[0,'BOS_R0']
        bmrc = df.loc[0,'BOS_RC']
        bmrd = df.loc[0,'BOS_RD']
        filterInfo = "Total RTD:%.3f,RT before Check Date:%.3f,RT after Check Date:%.3f,RT on the Check Date:%.3f" \
            % (bmrtd,bmr0,bmrc,bmrd)            
        print filterInfo
        
        filteTable = pandas.DataFrame(columns=table.columns) 
                
        for index, row in table.iterrows():
            symbol = row['symbol']
            srtd = row['BOS_RTD']
            sr0 = row['BOS_R0']
            src = row['BOS_RC']
            srd = row['BOS_RD']
            retRTD = True
            retR0 = True
            retRC = True
            retRD = True
            if self.crtd == 1:
                retRTD = (srtd >= bmrtd)
            if self.cr0 == 1:
                retR0 = (sr0 >= bmr0 )
            if self.crc == 1:
                retRC = (src >= bmrc)
            if self.crd == 1:
                retRD = (srd >= bmrd) 
            if (retRTD and retRTD and retRC and retRD):
                filteTable.loc[len(filteTable)+1]=row                
        
        print filteTable
        return filteTable
    '''        
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
        #info = "rsi=%.2f" %(self.rsi[-1])        
        return ""
    '''
    # process single date data        
    def procSingleData(self, index, ohlc):
        return
