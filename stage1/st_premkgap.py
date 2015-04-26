from collections import OrderedDict
import google_quote

class st_premkgap:
    def __init__(self):
        self.cleanup()
        self.stname = "st_premkgap" #strategy name
        self.googfin = google_quote.GoogleFinanceAPI()
        
    def cleanup(self):
        self.ind = OrderedDict()
        self.threshold = 2 # 2 percent
        return

    def usage(self):
        return "e.g. st_premktgap&gap=2"

        
    def setupParam(self,param):
        #do nothing
        return
        
    def algoFunc(self,px,premk_px):
        if abs(px/premk_px-1)>self.threshold:
            self.ind['gap'] = 1
        else:
            self.ind['gap'] = 0
        return
        
    # it is price data module(need real price data)
    def needPriceData(self):
        return True

    def getIndicators(self):
        return self.ind   
           
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)
        exg = param['exg']
        premk_px = self.googfin.get_rtpx(symbol,exg)['el']
        
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px,premk_px)
        
    def runScan(self,table):     
        return table                 