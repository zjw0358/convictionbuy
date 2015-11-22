'''
http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:sctr
Long-Term Indicators (weighting)

  * Percent above/below 200-day EMA (30%)
  * 125-Day Rate-of-Change (30%)

Medium-Term Indicators (weighting)

  * Percent above/below 50-day EMA (15%)
  * 20-day Rate-of-Change (15%)

Short-Term Indicators (weighting)

  * 3-day slope of PPO-Histogram (5%)
  * 14-day RSI (5%)

Percentage Price Oscillator (PPO): {(12-day EMA - 26-day EMA)/26-day EMA} x 100

Signal Line: 9-day EMA of PPO

PPO Histogram: PPO - Signal Line  

https://github.com/drewgriffith15/ThinkOrSwim/blob/master/SCTRSTUDY.ts
'''

from ind_base_px import BaseIndPx
import ind_ma
import ind_rsi
import st_pattern
import pandas

def calcChg(netchg, totchg):
    if (totchg != 0):
        chgRatio = (netchg / totchg)
    else:
        chgRatio = 0
    return chgRatio
    
class ind_sctr(BaseIndPx):
    def __init__(self):
        self.ind_ma = ind_ma.ind_ma()
        self.ind_rsi = ind_rsi.ind_rsi()
        self.pt = st_pattern.StrategyPattern()
        
    def usage(self):
        return "N/A"
        
    def calcPPO(self,ohlc):
        ema12 = pandas.ewma(ohlc['Adj Close'], span=12)
        ema26 = pandas.ewma(ohlc['Adj Close'], span=26)
        macd = ema12 - ema26
        ppo = (ema12 - ema26)/ema26*100;
        '''
        print "1 ==================="
        print ema12
        print "2 ==================="
        print ema26
        print "3 ==================="
        print ppo        
        return 1.2
        '''
        
        p1 = self.pt.weightMovAvg(ppo,3)
        p2 = pandas.Series(pandas.rolling_mean(ppo,3).tolist())
        #p2 = pandas.rolling_mean(ppo,3).reset_index(0).drop('index',axis=1)
        ppolinear = 6*(p1-p2)/(3-1)
        ppodiff = ppolinear - ppolinear.shift(1)        
        netChgAvg = pandas.rolling_mean(ppodiff, 3);
        totChgAvg = pandas.rolling_mean(abs(ppodiff), 3);        
        chgratio = pandas.Series(map(calcChg, netChgAvg,totChgAvg))
        shppo = 50 * (chgratio + 1) / 100;
        #print type(shppo),shppo
        #print type(shppo.get(len(shppo)-1))
        #get last element
        #print chgratio[-10:-1],
        #print ppolinear
        '''
        ohlc['ppo']=ppo
        ohlc['p1']=p1.tolist()
        ohlc['p2']=p2.tolist()
        ohlc['ppolinear']=ppolinear.tolist()
        print ohlc
        '''
        #print p1
        #print "============="
        #print shppo[-10:-1]*0.05
        return (shppo.get(len(shppo)-1))
        '''
        
        print "1 ==================="
        print netChgAvg
        print "2 ==================="
        print totChgAvg
        print "3 ==================="
        print chgratio
        print "4 ==================="
        '''
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        self.ind_ma.runIndicator(symbol,ohlc,param)
        rsidct={'cl':14}
        self.ind_rsi.runIndicator(symbol,ohlc,rsidct)

        #print lti200,ohlc['Adj Close'][-1],self.ind_ma.ind['ma200']      
        self.setupParam(param) #parent func
        self.algoFunc(ohlc)
                
    def algoFunc(self,ohlc):        
        lti200 = (ohlc['Adj Close'][-1] / self.ind_ma.ind['ma200'] -1)*100*0.3
        lti125 = (ohlc['Adj Close'][-1] / ohlc['Adj Close'][-125] -1)*100*0.3
        mti50 =  (ohlc['Adj Close'][-1] / self.ind_ma.ind['ma50'] -1)*100*0.15
        mti20 =  (ohlc['Adj Close'][-1] / ohlc['Adj Close'][-20] -1)*100*0.15
        stirsi = self.ind_rsi.ind['rsi']*0.05
        stippo = self.calcPPO(ohlc)*0.05
        
        score = lti200 + lti125 + mti50 + mti20 + stirsi + stippo
        #print "\t",lti200,lti125,mti50,mti20,stirsi,stippo
        self.ind['sctr'] = score
        return
        
        