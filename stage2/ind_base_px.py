'''
Base Indication class need price data
'''

from collections import OrderedDict
import marketdata

class BaseIndPx(object):        
    def __init__(self):
        #print "BaseIndPx init"
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
        return True

    def usage(self):
        return "This is Base indicator with Price data needed"
    
    # called in marketscan.py?
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
        return
    #return df & column list    
    
    def runScan(self,df):
        #print "self.param===",self.param
        col = df.columns.values 
        #print col,type(col)
        if not self.param:
            return df,col

        df,fcols = self.mtd.evalCriteria(df,self.param,col) 
        return df,fcols
    
