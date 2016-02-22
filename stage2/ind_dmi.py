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
#import time #to measure performance
#from collections import OrderedDict
from ind_base_px import BaseIndPx
from st_pattern import StrategyPattern

'''
def calcDX(row):
    if (row['pdi']+row['ndi'] > 0):
        return 100 * abs(row['pdi']-row['ndi'])/(row['pdi']-row['ndi'])
    else:
        return 0
'''
def calcDX2(pdi,ndi):
    if (pdi+ndi > 0):
        return 100 * abs(pdi-ndi)/(pdi+ndi)
    else:
        return 0

    
class ind_dmi(BaseIndPx):
    def usage(self):
        return "dmi=length"
 
    #much faster
    def algoFunc(self,df0):
        length = 14
        prevHigh = 0.
        prevLow = 0.
        plusDM = 0.
        minusDM = 0.
        index = 0
        tr=[]
        pdm=[]
        ndm=[]
        #ratio=[]
        sp = StrategyPattern()
        #debug
        #length = len(df0)-1
        #lastpx = df0['Adj Close'].iloc[len(df0)-1]

        ###
        #start = time.time()

        for row_index, row in df0.iterrows():
            #print index
            aclose = row['Adj Close']
            close = row['Close']
            high = row['High']
            low = row['Low']            
            tr.append(sp.trueRange(high, aclose, low))
            
            ###
            '''
            if (close>lastpx):
                r = (close-lastpx)/(length-index)
                ratio.append(r)
            else:
                ratio.append(0.)
            '''
            ####
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
                pdm.append(0.)
                ndm.append(0.)
                
            prevHigh = high
            prevLow = low
            index+=1
        '''        
        atr = sp.movingAverage(pandas.Series(tr),length)
        self.pdi = 100 * sp.movingAverage(pandas.Series(pdm),length) / atr
        self.ndi = 100 * sp.movingAverage(pandas.Series(ndm),length) / atr
        dx = self.pdi.combine(self.ndi,calcDX2)
        self.adx = sp.movingAverage(dx,length)
        '''
        atr1 = [float('nan') for _ in range(length-1)]
        atr2 = sp.wma(tr,length)
        atr = atr1 + atr2
        tmpPdi = atr1 + sp.wma(pdm,length)
        tmpNdi = atr1 + sp.wma(ndm,length)
        #print tmpPdi
        self.pdi = [100*ai/bi for ai,bi in zip(tmpPdi,atr)]
        self.ndi = [100*ai/bi for ai,bi in zip(tmpNdi,atr)]
        dx = map(calcDX2, self.pdi,self.ndi)
        self.adx = atr1 + sp.wma(dx,length)
        #debug
        #df0['ang'] = ratio

        df0['di+']=self.pdi
        df0['di-']=self.ndi
        df0['adx'] = self.adx

        #print df0
        pass  
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #print ohlc
        self.setupParam(param)     
        #self.close_px = ohlc['Adj Close']
        self.algoFunc(ohlc)        

    '''
    def runScan(self,table):
        return table
    '''
        