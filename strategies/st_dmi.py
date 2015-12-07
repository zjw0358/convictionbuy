'''
http://fs.591hx.com/Article/2012-03-31/0000034983s.shtml
'''

from ind_dmi import ind_dmi
from st_pattern import StrategyPattern
from trade_support import TradeSupport
import marketdata

'''
#move to st_pattern
def mergeSignal(b,s,c):
    if (b!=""):
        return b
    elif (s!=""):
        return s
    elif (c!=""):
        return c
    else:
        return ""
'''

class st_dmi(ind_dmi):
    '''
    def __init__(self):
        self.mtd = marketdata.MarketData()
    '''    
    def usage(self):
        return "dmi=length"


    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):        
        ind_dmi.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
  
    '''
    TODO probably there is a false signal,e.g crossbelow happen after buy signal,should we discard the buy signal?
    '''
    def algoStrategy(self,ohlc):
        sp = StrategyPattern()
        tsup = TradeSupport()
        buysg,sellsg = sp.divergencyCross(self.pdi, self.ndi, 2)
        closesg = sp.covergency(self.pdi, self.ndi, 2)
        
        #process these signale for backtest
        signal = map(sp.mergeSignal, buysg,sellsg,closesg)
        ohlc['signal'] = signal
        
        '''
        if (self.debug):
            ohlc['buysignal'] = buysg
            ohlc['sellsignal'] = sellsg
            ohlc['pdi'] = self.pdi
            ohlc['ndi'] = self.ndi
            ohlc['adx'] = self.adx
            print ohlc
        '''

        tsup.getLastSignal(buysg,sellsg, self.ind,'dmi_buy','dmi_sell')
        pass    
        
    # evaluate criteria string is more convenient   
    '''
    def runScan(self,df):
        col = df.columns.values 
        df = self.mtd.evalCriteria(df,self.param,col) 
        return df        
    '''
