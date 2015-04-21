from collections import OrderedDict

class st_perf:
    def __init__(self):
        self.cleanup()
        self.stname = "st_perf" #strategy name
        
    def cleanup(self):
        self.ind = OrderedDict()
        self.sgy = 1 # default sort all symbols 
        return

    def usage(self):
        return "available parameter:topperf;topperf_is,sort24,sort12,sort4,sort1,help"

        
    def setupParam(self,param):
        self.sgy = 1
        if 'topperf' in param:
            self.sgy = 1
        if "topperf_is" in param:
            self.sgy = 2
        if "sort24" in param:
            self.sgy = 3
        if "sort12" in param:
            self.sgy = 4
        if "sort4" in param:
            self.sgy = 5
        if "sort1" in param:
            self.sgy = 6
        return
          
    def algoFunc(self, px):
        p1d = 0
        p4w = 0
        p12w = 0
        p24w = 0
        pmax = 0
        plen = len(px)
        if plen >= 2:
            p1d = round((px[-1]/px[-2] - 1)*100,2) 
        if plen >= 4*7:
            p4w = round((px[-1]/px[-4*7] - 1)*100,2)
        if plen >= 12*7:
            p12w = round((px[-1]/px[-12*7] - 1)*100,2)
        if plen >= 24*7:
            p24w = round((px[-1]/px[-24*7] - 1)*100,2)
        if len(px) >= 1*7:
            p1w = round((px[-1]/px[-1*7] - 1)*100,2)

        pmax = round((px[-1]/px[0] - 1) * 100,2)
        
        
        self.ind['p1d'] = p1d
        self.ind['p1w'] = p1w  
        self.ind['p4w'] = p4w
        self.ind['p12w'] = p12w
        self.ind['p24w'] = p24w
        self.ind['pmax'] = pmax
        
    # it is price data module(need real price data)
    def needPriceData(self):
        return True
        
    def getIndicators(self):
        return self.ind    
            
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)
     
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        
 
 
    def runScan(self,table):        
        if self.sgy == 1:
            '''
            strategy top performance
            24 week top 20,12 week top 10,4 week top3 
            '''
            print "top performance screen.top in 24->12->4"
            df = table.sort_index(by='p24w',ascending=False).head(24).sort_index(by='p12w',ascending=False).head(10).sort_index(by='p4w',ascending=False).head(3)
        elif self.sgy == 2:
            '''
            strategy top performance meet all criteria
            24 week top 20,12 week top 10,4 week top3 
            '''
            print "top performance screen top in 24 & top in 12 & top in 4"
            #meet top3-4week,top10-12week,top20-24week together
            top4w = table.sort_index(by='p4w',ascending=False).head(3)['symbol']
            top12w = table.sort_index(by='p12w',ascending=False).head(10)['symbol']
            top24w = table.sort_index(by='p24w',ascending=False).head(24)['symbol']
            df = table[(table['symbol'].isin(top4w)) & (table['symbol'].isin(top12w)) & (table['symbol'].isin(top24w))]
        elif self.sgy == 3:
            '''
            sort 24week
            '''
            df = table.sort_index(by='p24w',ascending=False)
        elif self.sgy == 4:            
            #sort 12 week
            df = table.sort_index(by='p12w',ascending=False)
        elif self.sgy == 5:            
            #sort 4 week
            df = table.sort_index(by='p4w',ascending=False)
        elif self.sgy == 6:            
            #sort 1 week
            df = table.sort_index(by='p1w',ascending=False)

        return  df
        
      