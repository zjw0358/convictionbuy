'''
Base Indication class need price data
'''

from collections import OrderedDict
import marketdata

class BaseIndNoPx(object):        
    def __init__(self):
        #print "BaseIndNoPx init"
        self.mtd = marketdata.MarketData()
        self.cleanup()
    
    def cleanup(self):
        #print "BaseIndPx cleanup"
        self.ind = OrderedDict()
        self.debug = False   
        self.param = {}
             
    def getIndicators(self):
        return self.ind
        
    def needPriceData(self):
        return False

    def usage(self):
        return "This is Base indicator without Price data needed"
        
    def setupParam(self,param):
        '''        
        print "setup baseIndPx"
        self.mtd = marketdata.MarketData()
        self.param = {}
        self.cleanup()
        '''
        self.param = param
        if ('debug' in param):
            self.debug = True
        if ('verbose' in param):
            self.verbose = param['verbose']
        return

    def runIndicator(self,symbol,ohlc,param={}):
        #self.setupParam(param)
        pass
        
        
    def runScan(self,df):
        #print "self.param===",self.param
        col = df.columns.values 
        #print col,type(col)
        #if not self.param:
        #    return df,col

        df,fcols = self.mtd.evalCriteria(df,self.param,col) 
        return df,fcols
    
