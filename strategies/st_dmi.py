'''
http://fs.591hx.com/Article/2012-03-31/0000034983s.shtml
'''

from ind_dmi import ind_dmi
from st_pattern import StrategyPattern
from trade_support import TradeSupport

class st_dmi(ind_dmi):
    def usage(self):
        return "dmi=length"

    def setupParam(self,param):
        return        
            

    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        ind_dmi.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy()
        pass
        
    def algoStrategy(self):
        sp = StrategyPattern()
        tsup = TradeSupport()
        buysg,sellsg = sp.divergencyCross(self.pdi, self.ndi, 2)
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