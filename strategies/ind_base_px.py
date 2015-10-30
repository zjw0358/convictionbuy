'''
Base Indication class need price data
'''

from collections import OrderedDict
import marketdata

class BaseIndPx(object):
    def __init__(self):
        self.mtd = marketdata.MarketData()
        self.cleanup()
        
    def cleanup(self):
        #print "BaseIndPx cleanup"
        self.ind = OrderedDict()
        self.debug = False   
             
    def getIndicators(self):
        return self.ind
        
    def needPriceData(self):
        return True

    def usage(self):
        return "This is Base indicator with Price data needed"
        
    def setupParam(self,param):
        self.param = param
        if ('debug' in param):
            self.debug = True
        return
        
    def runScan(self,df):
        col = df.columns.values 
        df = self.mtd.evalCriteria(df,self.param,col) 
        return df 

