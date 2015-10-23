import pandas
import numpy

class StrategyPattern(object):
    def __init__(self):
        pass
        
    '''
    #to be deleted    
    def initData(self,fast,slow,offset):
        self.fast = fast
        self.slow = slow
        self.offset = offset
        pass
        
    def crossAbove(self):
        prevFast = self.fast[-self.offset]
        prevSlow = self.slow[-self.offset]
        signal = 65535 #float('nan')
        for idx, curSlow in enumerate(self.slow[-self.offset:]):
            #idx,-offset+idx
            currentFast = self.fast[-self.offset+idx]
            #print prevSlow,curSlow,prevFast,currentFast
            if (prevFast < prevSlow) and (currentFast > curSlow) :
                #signal = "True(%d)" % (self.offset-idx)
                signal = self.offset-idx
                #print "(buy)"
                # TODO
                #if (curSlow > prevSlow):
                #    signal += "*"
                #    print "****** strong signal********",signal
            prevFast = currentFast
            prevSlow = curSlow
        return signal
        
    def crossBelow(self):
        prevFast = self.fast[-self.offset]
        prevSlow = self.slow[-self.offset]
        signal = 65535 #float('nan')
        for idx, curSlow in enumerate(self.slow[-self.offset:]):
            #print idx,-offset+idx
            currentFast = self.fast[-self.offset+idx]
            if (prevFast > prevSlow) and (currentFast < curSlow):                
                #signal = "True(%d)" % (self.offset-idx)
                signal = self.offset-idx
            prevFast = currentFast
            prevSlow = curSlow
        return signal
    '''
    
    def cross(self, fast, slow, nbar):
        prevFast = fast[0]
        prevSlow = slow[0]
        buysg = []
        sellsg = []
        buyflag = False
        buycount = 1
        sellflag = False
        sellcount = 1
        
        for idx, curSlow in enumerate(slow):
            buysignal = ""
            sellsignal = ""
            currentFast = fast[idx]
            
            if (buyflag):
                #second round check
                if (currentFast > curSlow):
                    buycount+=1
                    if (buycount == nbar):
                        buysignal = "buy"
                        buyflag = False
                        buycount = 1
                else:
                    buyflag = False
                    buycount = 1
                pass
            else:
                if (prevFast < prevSlow) and (currentFast > curSlow) :
                    buyflag = True

            if (sellflag):
                 if (currentFast < curSlow):                
                     sellcount+=1
                     if (sellcount == nbar):
                        sellsignal = "sell"
                        sellcount = 1
                        sellflag = False
                 else:
                     sellcount = 1
                     sellflag = False
            else:            
                if (prevFast > prevSlow) and (currentFast < curSlow):                
                    sellflag = True      
                                        
            prevFast = currentFast
            prevSlow = curSlow
            buysg.append(buysignal)
            sellsg.append(sellsignal)
            
        return buysg,sellsg

        
        
    #fast cross above slow, and keep divengency moving at least n bars 
    #divergency cross
    def divergencyCross(self, fast, slow, nbar):
        prevFast = fast[0]
        prevSlow = slow[0]
        buysg = []
        sellsg = []
        buyflag = False
        buycount = 1
        sellflag = False
        sellcount = 1
        
        for idx, curSlow in enumerate(slow):
            #idx,-offset+idx
            buysignal = ""
            sellsignal = ""
            currentFast = fast[idx]
            #print idx,currentFast
            #print prevSlow,curSlow,prevFast,currentFast
            if (buyflag):
                if (currentFast > prevFast) and (curSlow < prevSlow):
                    buycount+=1
                    if (buycount == nbar):
                        #buysignal = self.offset-idx
                        buysignal = "buy"
                        buyflag = False
                        buycount = 1
                        #print "buy signal"
                else:
                    buyflag = False
                    buycount = 1
                pass
            else:
                if (prevFast < prevSlow) and (currentFast > curSlow) :
                    buyflag = True

            if (sellflag):
                 if (currentFast < prevFast) and (curSlow > prevSlow):                
                     sellcount+=1
                     if (sellcount == nbar):
                        sellsignal = "sell"
                        sellcount = 1
                        sellflag = False
                        #print "sell signal"
                 else:
                     sellcount = 1
                     sellflag = False
            else:            
                if (prevFast > prevSlow) and (currentFast < curSlow):                
                    sellflag = True      
                                        
            prevFast = currentFast
            prevSlow = curSlow
            buysg.append(buysignal)
            sellsg.append(sellsignal)
        
            
        return buysg,sellsg


    def trueRange(self,high,close,low):
        return max(max(high-low,abs(high-close)),abs(low-close))

    def sma(self,data,length):
        return pandas.stats.moments.rolling_mean(pandas.Series(data),length).tolist()      

    def ema(self, s, n):
        """
        returns an n period exponential moving average for
        the time series s
    
        s is a list ordered from oldest (index 0) to most
        recent (index -1)
        n is an integer
    
        returns a numeric array of the exponential
        moving average
        """
        s = numpy.array(s)
        ema = []
        j = 1
    
        #get n sma first and calculate the next n period ema
        sma = sum(s[:n]) / n
        multiplier = 2 / float(1 + n)
        ema.append(sma)
    
        #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
        ema.append(( (s[n] - sma) * multiplier) + sma)
    
        #now calculate the rest of the values
        for i in s[n+1:]:
            tmp = ( (i - ema[j]) * multiplier) + ema[j]
            j = j + 1
            ema.append(tmp)
    
        return ema

    #wilder moving average
    def wma(self, s, n):
        """
        returns an n period exponential moving average for
        the time series s
    
        s is a list ordered from oldest (index 0) to most
        recent (index -1)
        n is an integer
    
        returns a numeric array of the exponential
        moving average
        """
        s = numpy.array(s)
        ema = []
        j = 1
    
        #get n sma first and calculate the next n period ema
        sma = sum(s[:n]) / n
        multiplier = 1 / float(n)
        ema.append(sma)
    
        #EMA(current) = ( (Price(current) - EMA(prev) ) x Multiplier) + EMA(prev)
        ema.append(( (s[n] - sma) * multiplier) + sma)
    
        #now calculate the rest of the values
        for i in s[n+1:]:
            tmp = ( (i - ema[j]) * multiplier) + ema[j]
            j = j + 1
            ema.append(tmp)
    
        return ema
    
    