import pandas
import numpy as np

class StrategyPattern(object):
    def __init__(self):
        pass
  

    def mergeSignal(self, b,s,c):
        if (b!=""):
            return b
        elif (s!=""):
            return s
        elif (c!=""):
            return c
        else:
            return ""
            
    def combineAndSignal(self,*signals):
        siglen = len(signals)
        if (siglen ==1):
            return signals[0]
        if (len(signals) <1):
            return None

        newSigLst = []
        length = len(signals[0])

        for index in range(0, length):
            sigstr = signals[0][index]
            for sgidx in range(1, siglen):
                tocomp = signals[sgidx][index]
                if (tocomp!=sigstr):
                    print index,"not equal",sigstr,tocomp
                    sigstr=""
                    break;
            newSigLst.append(sigstr)
            
        return newSigLst
        
    #simplicity compare the two lines, fast>slow -> buy,verse vice sell
    def compare(self, fast, slow, nbar = 1, offset = 0):
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
            if idx>=offset:
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
                    if (currentFast > curSlow) :
                        if (buycount == nbar):
                            buysignal = "buy"
                            buyflag = False
                            buycount = 1
                        else:
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
                    if (currentFast < curSlow):
                        if (sellcount == nbar):
                            sellsignal = "sell"
                            sellcount = 1
                            sellflag = False
                        else:
                            sellflag = True      
                                        
            prevFast = currentFast
            prevSlow = curSlow
            buysg.append(buysignal)
            sellsg.append(sellsignal)
            
        return buysg,sellsg
  
    def supportline(self,pxlst,suppline,nbar=2):
        buyflag = False
        prevPx = pxlst[0]
        prevSup = suppline[0]
        upper=2.0
        lower=0.0
        buycount = 1
        buysg = []
        sellsg = []
        if (nbar<2):
            nbar=2
        
        for idx, curSupp in enumerate(suppline):
            curPx = pxlst[idx]
            curSupp = suppline[idx]
            buysignal = ""
            sellsignal = ""            
            if (buyflag):
                #second round check
                gap = (curPx-curSupp)*100/curSupp
                if (gap>lower): # simplicy px>support line
                    buycount+=1
                    if (buycount==nbar):
                        buysignal = "buy"
                        buyflag = False
                        buycount = 1
                else: #can't support at line
                        buyflag = False
                        buycount = 1
                pass
            else:
                if (prevPx>prevSup):
                    gap = (curPx-curSupp)*100/curSupp
                    if (gap<upper) and (gap>lower):
                        buyflag = True
                    pass
                    
            prevPx = curPx
            prevSup = curSupp
            buysg.append(buysignal)
            sellsg.append(sellsignal)

        return buysg,sellsg
        
    #fast cross above slow line  - buy (and keep n bar)
    #fast cross below slow line  - sell
    def cross(self, fast, slow, nbar = 1,offset = 0):
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
            if (idx>=offset):
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
                        if (buycount == nbar):
                            buysignal = "buy"
                            buyflag = False
                            buycount = 1
                        else:
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
                        if (sellcount == nbar):
                            sellsignal = "sell"
                            sellcount = 1
                            sellflag = False
                        else:
                            sellflag = True       
                                        
            prevFast = currentFast
            prevSlow = curSlow
            buysg.append(buysignal)
            sellsg.append(sellsignal)
            
        return buysg,sellsg

    #e.g rsi crossabove 30 means buy signal
    # rsi crossabove 70 means sell signal
    def crossValue(self, bline, sline, buyValue, sellValue, nbar):
        prevBuy = bline[0]
        prevSell = sline[0]
        buysg = []
        buyflag = False        
        buycount = 1
        
        sellsg = []
        sellflag = False        
        sellcount = 1
        
        
        for idx, currentBuy in enumerate(bline):
            buysignal = ""
            sellsignal = ""
            #print "pattern",idx,currentBuy
            currentSell = sline[idx]
                        
            if (buyflag):
                #second round check
                if (currentBuy > buyValue):
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
                if (prevBuy < buyValue) and (currentBuy > buyValue) :
                    if (buycount == nbar):
                            buysignal = "buy"
                            buyflag = False
                            buycount = 1
                    else:
                        buyflag = True
                    

            if (sellflag):
                 if (currentSell < sellValue):                
                     sellcount+=1
                     if (sellcount == nbar):
                        sellsignal = "sell"
                        sellcount = 1
                        sellflag = False
                 else:
                     sellcount = 1
                     sellflag = False
            else:            
                if (prevSell > sellValue) and (currentSell < sellValue):     
                    if (sellcount == nbar):
                            sellsignal = "sell"
                            sellcount = 1
                            sellflag = False
                    else:
                        sellflag = True                  
         
          
                                        
            prevBuy = currentBuy
            prevSell = currentSell
            buysg.append(buysignal)
            sellsg.append(sellsignal)
            
        return buysg,sellsg

    # fast and slow covergency, used to find 'close' signal
    def covergency(self,fast,slow,nbar):
        prevFast = fast[0]
        prevSlow = slow[0]
        entryThr = 10        
        closesg = []
        closeflag = False
        count = 1
        
        for idx, curSlow in enumerate(slow): 
            closesignal = ""
            currentFast = fast[idx]
            prevDiff = abs(prevFast-prevSlow)
            curDiff = abs(currentFast-curSlow)            
            
            if (closeflag):
                #fast crossbelow slow? rarely happen in short time                                
                # ADX?
                if (curDiff < prevDiff):
                    count+=1
                    if (count == nbar):
                        closesignal = "close"
                        closeflag = False
                        count = 1
                        #print "buy signal"
                else:
                    closeflag = False
                    count = 1
                    
            else:
                if (prevDiff > entryThr and curDiff < prevDiff):
                    closeflag = True

            prevFast = currentFast
            prevSlow = curSlow
            closesg.append(closesignal)
            
        return closesg
        
    # fast and slow covergency, used to find 'close' signal
    # fast and slow drop, but fast drop further
    def covergency1(self,fast,slow):
        prevFast = fast[0]
        prevSlow = slow[0]
        closesg = []
        closeflag = False
        difftgr = 0.3
        fstgr = 0.999
        
        for idx, curSlow in enumerate(slow): 
            closesignal = ""
            currentFast = fast[idx]
            prevDiff = abs(prevFast-prevSlow)
            curDiff = abs(currentFast-curSlow)            
            '''
            and curDiff/prevDiff < error
            and currentFast/prevFast < error
            and curSlow/prevSlow < error
            '''      
            if (curDiff < prevDiff and currentFast < prevFast and curSlow < prevSlow 
                and curDiff/prevDiff < difftgr
                and currentFast/prevFast < fstgr
                and curSlow/prevSlow < fstgr):
                #print curDiff/prevDiff,currentFast/prevFast,curSlow < prevSlow
                #closesignal = "close%f,%f,%f" %(curDiff/prevDiff,currentFast/prevFast,curSlow/prevSlow)
                closesignal = " close"
            prevFast = currentFast
            prevSlow = curSlow
            closesg.append(closesignal)
            
        return closesg
         
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
        s = np.array(s)
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

    def lastWeightMovAvg(self,lst,period):
        data = np.average(lst[-period:], weights=range(period,0,-1))
        return data

    #generate temporary list
    def weightMovAvg(self,lst,period):
        data = []
        for index in range(0,len(lst)):
            if index < (period-1):
                #print index,"add nan"
                data.append(float('nan'))
            else:
                d = np.average(lst[index+1-period:index+1], weights=range(period,0,-1))
                data.append(d)
                #print index,"add",d
        return pandas.Series(data,index=lst.index)
        
    def weightMovAvg0(self,lst,period):
        
        data = []
        for index in range(0,len(lst)):
            if index < (period-1):
                #print index,"add nan"
                data.append(float('nan'))
            else:
                d = np.average(lst[index+1-period:index+1], weights=range(period,0,-1))
                data.append(d)
                #print index,"add",d
        return pandas.Series(data)
                   
    #TODO not try this method yet
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
    
    