# -*- coding: utf-8 -*-
import math
import pandas
from collections import defaultdict
import operator
#import tradesupport
#import simutable
#import numpy


class st_quotient:
    def __init__(self,bt):
        self.cleanup()
        self.stname = "quotient" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()


    def getStrategyName(self):
        return self.stname
    
    # called this when doing automation test
    def cleanup(self):
        self.hplst=[]
        self.filtlst=[]
        self.nrflst=[]
        self.quolst=[]
        self.shortquolst=[]
        self.peaklst=[]
        self.pricelst=[]
        
    def setup(self,k1,k2,cl):
        self.cleanup() #must call cleanup before test
        self.k1=k1
        self.k2=k2
        self.cutoffLength = cl  
        self.alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
        self.a1 = math.exp(-1.414 * math.pi / self.cutoffLength);
        self.b1 = 2 * self.a1 * math.cos(math.radians(1.414 * 180 / self.cutoffLength));
        self.c2 = self.b1
        self.c3 = - self.a1**2
        self.c1 = 1 - self.c2 - self.c3;
        self.setupInfo = \
        "=== ST_QUOTIENT SETUP===========================================\n" + \
        "k1=%.2f\n" % self.k1 + \
        "k2=%.2f\n" % self.k2 + \
        "cutoff length=%d\n" % self.cutoffLength + \
        "alpha1=,",self.alpha1
        print "(1 - alpha1 / 2)*(1 - alpha1 / 2),",(1 - self.alpha1 / 2)*(1 - self.alpha1 / 2) 
        print "a1,",self.a1
        print "b1,",self.b1
        print "c1,",self.c1
        print "c2,",self.c2
        print "c3,",self.c3  
        print "================================================================"
    def setupParam(self,param):
        # default parameter
        k1 = 0.7
        k2 = 0.4
        cl = 25
        if 'k1' in param:
            k1 = float(param['k1'])
        if 'k2' in param:
            k2 = float(param['k2'])
        if 'cl' in param:
            cl = int(param['cl'])
        self.setup(k1,k2,cl)
                
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

    # strategy, find the buy&sell signal
    def runStrategy(self,symbol,ohlc,param={}):
        #initialize tradesupport
        if len(param) != 0:
            self.setupParam(param)
        self.tradesup.beginTrade(self.setupInfo, symbol, ohlc) 
        
        close_px = ohlc['Adj Close']
        
        # loop checking close price
        for index in range(0, len(close_px)):
            self.tradesup.processData(index)  # must be places at first          
            self.procSingleData(index,close_px[index]) # the algorithm
            self.tradesup.calcDailyValue(index) # update daily value
            
        #call this to create daily value data frame
        self.tradesup.createDailyValueDf()

    # automation optimization test
    def runOptimization(self,symbol,ohlc,bm):
        length = range(10, 60, 5)
        k1set = [x * 0.1 for x in range(6, 10)]
        k2set = [x * 0.1 for x in range(1, 5)]
        
        #must setup report tool before simulation test
        self.simutable.setupSymbol(symbol,bm)

        for k2 in k2set:
            for k1 in k1set: 
                for cl in length:
                    #self.cleanup() # in automation optimization must call cleanup before test
                    self.setup(k1,k2,cl)
                    self.runStrategy(symbol,ohlc)
                    
                    # to generate simulation report
                    param = "k1=%.1f&k2=%.1f&cl=%d"%(k1,k2,cl)
                    self.simutable.addOneTestResult(self.setupInfo,param,self.tradesup.getDailyValue())
        
        #add results to report
        self.simutable.makeSimuReport()
        self.tradesup.setDailyValueDf(self.simutable.getBestDv())

    ############################################################################
    # ALGORITHM
    ############################################################################            
    def EhlersSuperSmootherFilter(self,hp0,hp1,filt1,filt2):
        filt =  self.c1 * (hp0 + hp1) / 2 + self.c2 * filt1 + self.c3 * filt2;
        return filt


    # process single date data        
    def procSingleData(self,index,price):
        self.hplst.append(0.)
        self.filtlst.append(0.)
        self.peaklst.append(0.)
        self.quolst.append(0.)
        self.shortquolst.append(0.)
        self.nrflst.append(0.)
        self.pricelst.append(price)
        price1=0.
        price2=0.
        hp1=0.
        hp2=0.
        filt1=0.
        filt2=0.
        peak1=0.
        
        if index >=1:
            price1= self.pricelst[index-1]
            hp1 = self.hplst[index-1]
            filt1 = self.filtlst[index-1]
            peak1 = self.peaklst[index-1]
            if index >= 2:
                price2= self.pricelst[index-2]
                hp2 = self.hplst[index-2]
                filt2 = self.filtlst[index-2]                
    
        hp0 = (1 - self.alpha1 / 2)*(1 - self.alpha1 / 2) * (price - 2 * price1 + price2) + 2 * (1 - self.alpha1) * hp1 - (1 - self.alpha1)*(1 - self.alpha1) * hp2;
        self.hplst[index]=hp0
                
        filt = self.EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2);
        self.filtlst[index]=filt
        
        #fast attack            
        peak0 = peak1*0.991
        
        af = abs(filt)
        if af > peak0:
            peak0 = af
        self.peaklst[index] = peak0
        
        NormRoofingFilter = filt / peak0;
        Quotient1 = (NormRoofingFilter + self.k1) / (self.k1 * NormRoofingFilter + 1);
        Quotient2 = (NormRoofingFilter + self.k2) / (self.k2 * NormRoofingFilter + 1);
        
        self.quolst[index]=Quotient1
        self.shortquolst[index]=Quotient2
        
        self.nrflst[index]=NormRoofingFilter
        
        #must be placed before trigger signal(to avoid buying ahead)
        #self.support.processData(index)            

        prevQuotient = self.quolst[index-1]
        prevShortQuo = self.shortquolst[index-1]
        
        # trading signal
        if prevQuotient<0 and Quotient1>=0:
            #print "quotient buy@",index
            self.tradesup.buyorder(self.stname)
                
        if prevShortQuo>0 and Quotient2<=0:
            #print "quotient sell@",index
            self.tradesup.sellorder(self.stname)
      
  
    #draw curve            
    def drawChart(self,ax,sdatelabel):
        ax.set_ylim([-1,1])
        ax.set_yticks([-0.5,0.5])
        ax.plot(sdatelabel[self.offset:], self.df['quo1'][self.offset:])
        ax.plot(sdatelabel[self.offset:], self.df['quo2'][self.offset:])
        ax.axhline(0, color='r')
     
