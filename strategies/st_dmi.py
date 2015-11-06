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
    def __init__(self):
        self.mtd = marketdata.MarketData()
        
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
        signal = map(mergeSignal, buysg,sellsg,closesg)
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

    #difficult to directly use criteria string
    #criteria doesn't know 'or'
    # buy<20 | sell<30
    def runScan0(self,table):
        mode = 0
        if 'buy' in self.param:
            bl = int(self.param['buy'])
            mode = mode|1
        if 'sell' in self.param:
            sl = int(self.param['sell'])
            mode = mode|2
            
        if (mode==1):
            table = table[(table['dmi_buy'] < bl)]
        elif (mode==2):
            table = table[(table['dmi_sell'] < sl)]
        elif (mode==3):
            table = table[(table['dmi_buy'] < bl) | (table['dmi_sell'] < sl)]

        return table

    # evaluate criteria string is more convenient   
    def runScan(self,df):
        col = df.columns.values 
        df = self.mtd.evalCriteria(df,self.param,col) 
        return df        
