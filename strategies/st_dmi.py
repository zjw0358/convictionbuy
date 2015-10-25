'''
http://fs.591hx.com/Article/2012-03-31/0000034983s.shtml
'''

from ind_dmi import ind_dmi
from st_pattern import StrategyPattern
from trade_support import TradeSupport

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

class st_dmi(ind_dmi):
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
        
        #To be deleted
        ohlc['buy'] = buysg
        ohlc['sell'] = sellsg

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
        #print buysg
        #print ["%s\n" % item  for item in buysg]        
        #print sellsg
        
        idx,sig = tsup.getLastSignal(buysg,sellsg)
        sigstr = "%s(%d)" % (sig,idx)
        if (sig=="buy"):            
            self.ind['dmi_buy'] = sigstr
        else:
            self.ind['dmi_sell'] = sigstr
        pass    

    def runScan(self,table):
        return table
        