#import numpy as np
from ind_base_px import BaseIndPx
'''
an expert of a system
=== A EXPERT OF A SYSTEM SETUP==================================
technical analysis of stock and commodity 
2013 oct
'''
class ind_aeoas(BaseIndPx):
    def usage(self):
        return "t=length&h=length(typical,heikin-ashi)"
        
    '''
    "typical period=%d,%.3f,%.3f\n" % (typWin,self.typema1,self.typema2) + \
    "heikin-ashi period=%d,%.3f,%.3f\n" % (hacWin,self.hacema1,self.hacema2) + \
    '''
    def setupParam(self,param):
        BaseIndPx.setupParam(self,param)
        self.typWin = 5
        self.hacWin = 8

        if 't' in param:
            self.typWin = float(param['t'])
        if 'h' in param:
            self.hacWin = float(param['h'])            
            
        self.typema1 = 2.0/(self.typWin+1)
        self.typema2 = 1 - self.typema1
        self.hacema1 = 2.0/(self.hacWin+1)
        self.hacema2 = 1 - self.hacema1        
        
    def algoFunc(self,ohlc):
        haopenLst=[]
        #haCLst=[]
        #self.typicalLst=[]
        self.avgTypEmaLst=[]
        self.avgHacEmaLst=[]
        
#        for index, row in ohlc.iterrows():
        row0 = ohlc.iloc[0]
        prevAvg = (row0['High'] + row0['Low'] + row0['Close'] + row0['Open'])/4
        #prevAvg = (ohlc['High'].iloc[0] + self.ohlc['Low'].iloc[index-1] + self.ohlc['Close'].iloc[index-1] + self.ohlc['Open'].iloc[index-1])/4
        #start from 1
        
#        for index in range(0, len(ohlc)):
        #index = 0
        #for index, row in ohlc.iterrows():
        for index in range(0, len(ohlc)):
            highv = float(ohlc.iloc[index]['High'])
            lowv = float(ohlc.iloc[index]['Low'])
            openv = float(ohlc.iloc[index]['Open'])
            closev = float(ohlc.iloc[index]['Close'])
            currAvg = (highv + lowv + closev + openv)/4
            typical = (highv + lowv + closev) / 3

            if index > 0:
                haOpen = (prevAvg + haopenLst[index-1])/2
                avgTyp = typical * self.typema1 + self.typema2 * self.avgTypEmaLst[index-1]
            else:
                haOpen = 0
                avgTyp = typical

            haC = (currAvg + haOpen + max(highv,haOpen) + min(lowv, haOpen)) / 4
            
            if index > 0:
                avgHac = haC*self.hacema1 + self.hacema2 * self.avgHacEmaLst[index-1]
            else:
                avgHac = haC
                
            prevAvg = currAvg
            #index += 1
            #haCLst.append(haC)
            haopenLst.append(haOpen)
            #typicalLst.append(typical)
            self.avgTypEmaLst.append(avgTyp)
            self.avgHacEmaLst.append(avgHac)
        ohlc['avgt'] = self.avgTypEmaLst
        ohlc['hac'] = self.avgHacEmaLst
        #print ohlc
      
       
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)     
        self.ohlc = ohlc
        self.algoFunc(self.ohlc)