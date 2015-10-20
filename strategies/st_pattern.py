import pandas
import numpy

class StrategyPattern(object):
    def __init__(self):
        pass
        
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
    
    #fast cross above slow, and keep divengency moving at least n bars
    def divCross(self, nbar):
        prevFast = self.fast[-self.offset]
        prevSlow = self.slow[-self.offset]
        buysignal = 65535
        sellsignal = 65535
        buyflag = False
        buycount = 1
        sellflag = False
        sellcount = 1
        for idx, curSlow in enumerate(self.slow[-self.offset:]):
            #idx,-offset+idx
            currentFast = self.fast[-self.offset+idx]
            #print prevSlow,curSlow,prevFast,currentFast
            if (buyflag):
                if (currentFast > prevFast) and (curSlow < prevSlow):
                    buycount+=1
                    if (buycount == nbar):
                        buysignal = self.offset-idx
                        print "buy signal",buysignal
                else:
                    buyflag = False
                    buycount = 1
                pass
            else:
                if (prevFast < prevSlow) and (currentFast > curSlow) :
                    #signal = "True(%d)" % (self.offset-idx)
                    buyflag = True
            if (sellflag):
                 if (currentFast < prevFast) and (curSlow > prevSlow):                
                     sellcount+=1
                     if (sellcount == nbar):
                        sellsignal = self.offset-idx
                        print "sell signal",buysignal
                 else:
                     sellcount = 1
                     sellflag = False
            else:            
                if (prevFast > prevSlow) and (currentFast < curSlow):                
                    sellflag = True                          
            prevFast = currentFast
            prevSlow = curSlow
        return buysignal,sellsignal

    def trueRange(self,high,close,low):
        return max(max(high-low,abs(high-close)),abs(low-close))

    def movingAverage(self,data,length):
        return pandas.stats.moments.rolling_mean(data,length) #.tolist()      

    def ema(s, n):
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