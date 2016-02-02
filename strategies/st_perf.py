from collections import OrderedDict
from ind_base_px import BaseIndPx

class st_perf(BaseIndPx): 
    def usage(self):
        usage = "available parameter:\n"
        usage += "\ttopperf: select from 24 week top 20->12 week top 10->4 week top3 \n"
        usage += "\ttopperf_is: meet all criteria, must be in 24 week top 20,12 week top 10,4 week top3 \n"
        usage += "\tsort24:sort by past 24 weeks performance\n"
        usage += "\tsort12:by past 12 weeks\n"
        usage += "\tsort4:by past 4 weeks\n"
        usage += "\tsort1:by past 1 weeks\n"        
        return usage

    #override func
    def setupParam(self,param):
        BaseIndPx.setupParam(self,param)                
        self.sgy = 1
        #print param
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
        if "sorts" in param:
            self.sgy = 7
            #print "select sorts"
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
            
    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)
     
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)     
 
    def runScan(self,table): 
        # total return
        retmax = table['pmax'].sum()
        ret1w =  table['p1w'].sum()
        ret4w =  table['p4w'].sum()
        ret12w =  table['p12w'].sum()
        ret24w =  table['p24w'].sum()
        '''
        print "return max",retmax
        print "return 1 week",ret1w
        print "return 4 week",ret4w
        print "return 12 week",ret12w
        print "return 24 week",ret24w
        '''                                                             
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
            #sort 24 week            
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
        elif self.sgy == 7:
            df = table.sort_index(by='symbol',ascending=True)
            #df = table[(table['p4w']-table['p12w']>1) &(table['p4w']-table['p12w']<3) & (table['p4w']>2) & (table['p4w']<5)]
            pass
        cols = df.columns.values 
        return  df,cols
        
      