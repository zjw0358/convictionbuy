'''
marketscan zack module
fileter zack data file by abr(average broker recommadation) and ER estimate
use case:
    
'''
import data_zacks
import marketdata
import pandas
import ms_config
import sys
from collections import OrderedDict
from ind_base_nopx import BaseIndNoPx

class st_zack(BaseIndNoPx):
    def __init__(self):
        self.zack = data_zacks.data_zacks()
        self.mtd = marketdata.MarketData()
        self.cfg = ms_config.MsDataCfg("")
        self.zackfile = self.cfg.getDataConfig("zack")
        self.cachefolder = self.cfg.getDataConfig("cache","../cache/")
        self.hasCachedDF = False
        BaseIndNoPx.__init__(self)
        return    
        
    def usage(self):
        print "ms_zack_data $abr $estm"

    def loadData(self,fileName):
        df = self.zack.loadZackCsvFile(fileName)
        return df
        
    # no need real price data
    #def needPriceData(self):
    #    return False
        
    def loadNextErd(self,df):
        for index, row in df.iterrows():
            symbol = row['symbol']
            #print "reading erd",symbol
            fn = self.cachefolder + symbol + "_erdate.erd"
            try:
                if (self.verbose>1):
                    print "reading erd",symbol,"\ttopen file",fn
                with open(fn, "r") as fp:
                    erd = fp.readline()
                    df.loc[index,'erd'] = erd[:-1]
            except:
                print symbol,"no earning date, set it with empty value"
                df.loc[index,'erd'] = ""
        return df


    #def process(self,tablein,param0):
    def process(self,tablein):
        #self.setupParam(param0)
        #"$eracc2":"epsq1e/epsqtr-3>epsqtr0/epsqtr-4&epsqtr0/epsqtr-4>epsqtr-1/epsqtr-5&epsqtr-1/epsqtr-5>epsqtr-2/epsqtr-6",
        ticklist = tablein['symbol']
        param = OrderedDict()
        macro = {
            "$abr":"epsqtr0/epsqtr-1>epsqtr-1/epsqtr-2&epsqtr-1/epsqtr-2>epsqtr-2/epsqtr-3&epsq1e/epsqtr0>epsqtr0/epsqtr-1",           
        }
        #replace keyword in parameter
        for pa in self.param:
            if pa in macro:
                crlst = macro[pa].split("&")                            
                for cr in crlst:
                    param[cr]=""
            else:
                param[pa]=""
                

        #print "st_zack parameter=",param        
        col = ['symbol']            

        if (not self.hasCachedDF):
            df = self.loadData(self.zackfile)
            # erd
            df = self.loadNextErd(df)
            self.cacheDF = df
            self.hasCachedDF = True
        else:
            df = self.cacheDF
            pass

        #no criteria, select all columns
        if len(param)==0:
            #df = df[col]
            pass
        else:
            df,cols = self.mtd.evalCriteria(df,param,col)
      
          
        df1 = pandas.merge(tablein,df,how='inner')
        #cols = df1.columns.values
        #print df1
        return df1,cols
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = st_zack()
    obj.test()