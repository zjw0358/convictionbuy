'''
marketscan zack module
fileter zack data file by abr(average broker recommadation) and ER estimate
use case:
    
'''
import zack_data
import marketdata
import pandas
import ms_config
import sys
from collections import OrderedDict

class ms_zack:
    def __init__(self):
        self.zack = zack_data.zack_data()
        self.mtd = marketdata.MarketData()
        self.cfg = ms_config.MsDataCfg("")
        self.zackfile = self.cfg.getDataConfig("zack")
        self.cachefolder = self.cfg.getDataConfig("folder")
        #print self.cachefolder
        return    
        
    def usage(self):
        print "ms_zack_data $abr $estm"

    def loadData(self,fileName):
        df = self.zack.loadZackCsvFile(fileName)
        return df
        
    # no need real price data
    def needPriceData(self):
        return False
        
    def loadNextErd(self,df):
        for index, row in df.iterrows():
            symbol = row['symbol']
            print "reading erd",symbol
            fn = self.cachefolder + symbol + "_erdate.erd"
            try:
                print "\topen file",fn
                with open(fn, "r") as fp:
                    erd = fp.readline()
                    df.loc[index,'erd'] = erd[:-1]
            except:
                print "\tset erd with empty value"
                df.loc[index,'erd'] = ""
        return df
        
    def process(self,tablein,param0):
        #"$eracc2":"epsq1e/epsqtr-3>epsqtr0/epsqtr-4&epsqtr0/epsqtr-4>epsqtr-1/epsqtr-5&epsqtr-1/epsqtr-5>epsqtr-2/epsqtr-6",
        ticklist = tablein['symbol']
        param = OrderedDict()
        macro = {
            "$abr":"epsqtr0/epsqtr-1>epsqtr-1/epsqtr-2&epsqtr-1/epsqtr-2>epsqtr-2/epsqtr-3&epsq1e/epsqtr0>epsqtr0/epsqtr-1",
           
        }
        #replace keyword in parameter
        for pa in param0:
            if pa in macro:
                crlst = macro[pa].split("&")                            
                for cr in crlst:
                    param[cr]=""
            else:
                param[pa]=""
                

        print "ms_zack parameter=",param
        
        col = ['symbol']            
        df = self.loadData(self.zackfile)
        df = self.loadNextErd(df)
        print df
        sys.exit()
        #no criteria
        if len(param)==0:
            df = df[col]
        else:
            df,cols = self.mtd.evalCriteria(df,param,col)        
        df1 = pandas.merge(tablein,df,how='inner')
        # erd
        # df1 = self.loadNextErd(df1)
        return df1  
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_zack()
    obj.test()