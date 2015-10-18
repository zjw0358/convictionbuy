'''
calculate DMI
#
# TD Ameritrade IP Company, Inc. (c) 2008-2015
#

declare lower;

input length = 14;
input averageType = AverageType.WILDERS;

def hiDiff = high - high[1];
def loDiff = low[1] - low;

def plusDM = if hiDiff > loDiff and hiDiff > 0 then hiDiff else 0;
def minusDM =  if loDiff > hiDiff and loDiff > 0 then loDiff else 0;

def ATR = MovingAverage(averageType, TrueRange(high, close, low), length);
plot "DI+" = 100 * MovingAverage(averageType, plusDM, length) / ATR;
plot "DI-" = 100 * MovingAverage(averageType, minusDM, length) / ATR;

def DX = if ("DI+" + "DI-" > 0) then 100 * AbsValue("DI+" - "DI-") / ("DI+" + "DI-") else 0;
plot ADX = MovingAverage(averageType, DX, length);

"DI+".SetDefaultColor(GetColor(1));
"DI-".SetDefaultColor(GetColor(8));
ADX.SetDefaultColor(GetColor(5));
'''
import pandas
from collections import OrderedDict
from ind_base_px import BaseIndPx

class ind_dmi(BaseIndPx):
    def usage(self):
        return "dmi=length"

    def setupParam(self,param):
        return
        
    def trueRange(self,high,close,low):
        return max(max(high-low,abs(high-close)),abs(low-close))

    def movingAverage(self,data,length):
        return pandas.stats.moments.rolling_mean(data,length) #.tolist()      
        
    def algoFunc1(self,df):
        length = 14
        tr = []
        pdm = []
        ndm = []
        prevHigh = 0.
        prevLow = 0.
        plusDM = 0.
        minusDM = 0.
        index = 1
        for row_index, row in df.iterrows():
            #print index
            close = row['Adj Close']
            high = row['High']
            low = row['Low']            
            tr.append(self.trueRange(high, close, low))
            if (index>0):
                hiDiff = high - prevHigh
                loDiff = prevLow - low

                if hiDiff > loDiff and hiDiff > 0:
                    plusDM = hiDiff
                else:
                    plusDM = 0;
                    
                if loDiff > hiDiff and loDiff > 0:
                    minusDM = loDiff
                else:
                    minusDM = 0;
                    
                pdm.append(plusDM)
                ndm.append(minusDM)
            else:
                prevHigh = high
                prevLow = low
            index+=1
                                
        s = pandas.Series(tr[1:], index=df.index[1:]) 
        p = pandas.Series(pdm, index=df.index[1:]) 
        n = pandas.Series(ndm, index=df.index[1:]) 
        atr = self.movingAverage(s,length)
        pdi = 100*self.movingAverage(p,length) / atr
        ndi = 100*self.movingAverage(n,length) / atr
        

        
        
        print pdi
        print ndi
        #print n       
        pass  
            
    def algoFunc(self,df):
        length = 14
        tr = []
        pdm = []
        ndm = []
        prevHigh = 0.
        prevLow = 0.
        plusDM = 0.
        minusDM = 0.
        index = 0
        for row_index, row in df.iterrows():
            #print index
            close = row['Adj Close']
            high = row['High']
            low = row['Low']            

            #tr.append(self.trueRange(high, close, low))
            df.loc[row_index,'tr'] = self.trueRange(high, close, low)     
            
            if (index>0):
                hiDiff = high - prevHigh
                loDiff = prevLow - low
                if hiDiff > loDiff and hiDiff > 0:
                    plusDM = hiDiff
                else:
                    plusDM = 0;
                    
                if loDiff > hiDiff and loDiff > 0:
                    minusDM = loDiff
                else:
                    minusDM = 0;
                print row_index, index, high,prevHigh, low, prevLow,hiDiff,loDiff,plusDM
                df.loc[row_index,'pdm'] = plusDM   
                df.loc[row_index,'ndm'] = minusDM          
                #pdm.append(plusDM)
                #ndm.append(minusDM)
            else:
                df.loc[row_index,'pdm'] = 0   
                df.loc[row_index,'ndm'] = 0    
            prevHigh = high
            prevLow = low
            index+=1
      
        atr = self.movingAverage(df['tr'],length)
        pdi = 100*self.movingAverage(df['pdm'],length) / atr
        ndi = 100*self.movingAverage(df['ndm'],length) / atr
        df['pdi'] = pdi          
        df['ndi'] = ndi  
        #s = pandas.Series(tr[1:], index=df.index[1:]) 
        #p = pandas.Series(pdm, index=df.index[1:]) 
        #n = pandas.Series(ndm, index=df.index[1:]) 
        #atr = self.movingAverage(s,length)
        #pdi = 100*self.movingAverage(p,length) / atr
        #ndi = 100*self.movingAverage(n,length) / atr
        #print pdi
        #print ndi
        print df
        #print n       
        pass  

    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        print ohlc
        self.setupParam(param)     
        self.close_px = ohlc['Adj Close']
        self.algoFunc(ohlc)        

    def runScan(self,table):
        return table