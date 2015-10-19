'''
http://fs.591hx.com/Article/2012-03-31/0000034983s.shtml
'''

from ind_dmi import ind_dmi
from st_pattern import StrategyPattern

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
        #sp.initData(self.inddf['pdi'], self.inddf['ndi'], 50)
        sp.initData(self.pdi.tolist(), self.ndi.tolist(), 50)
        buysg,sellsg = sp.divCross(2)
        self.ind['dmi_buy'] = buysg
        self.ind['dmi_sell'] = sellsg
        pass    

    def runScan(self,table):
        return table