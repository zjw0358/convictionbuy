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

'''

from ind_base_px import BaseIndPx
import ind_ma
import ind_rsi

class ind_sctr(BaseIndPx):
    def __init__(self):
        self.ind_ma = ind_ma.ind_ma()
        self.ind_rsi = ind_rsi.ind_rsi()
        
    def usage(self):
        return "sctr=length"
        
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        self.ind_ma.runIndicator(symbol,ohlc,param)
        rsidct={'cl':14}
        self.ind_rsi.runIndicator(symbol,ohlc,rsidct)
        lti200 = (ohlc['Adj Close'][-1] / self.ind_ma.ind['ma200'] -1)*100*0.3
        lti125 = (ohlc['Adj Close'][-1] / ohlc['Adj Close'][-125] -1)*100*0.3
        mti50 =  (ohlc['Adj Close'][-1] / self.ind_ma.ind['ma50'] -1)*100*0.15
        mti20 =  (ohlc['Adj Close'][-1] / ohlc['Adj Close'][-20] -1)*100*0.15
        stirsi = self.ind['rsi']*0.05
        
        #print lti200,ohlc['Adj Close'][-1],self.ind_ma.ind['ma200']      
        self.setupParam(param) #parent func
        self.algoFunc(ohlc)
                
    def algoFunc(self,df0):
        return
        