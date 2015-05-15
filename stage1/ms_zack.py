'''
marketscan zack module
fileter zack data file by abr(average broker recommadation) and ER estimate
use case:
    
'''
import zack_data
import marketdata
import pandas
from collections import OrderedDict

class ms_zack:
    def __init__(self):
        self.zack = zack_data.zack_data()
        self.zackfile = "./msdata_zack.csv"
        self.mtd = marketdata.MarketData()
        return    
        
    def usage(self):
        print "ms_zack_data $abr $estm"

    def loadData(self,fileName):
        df = self.zack.loadZackCsvFile(fileName)
        return df
        
    # no need real price data
    def needPriceData(self):
        return False
        
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
        
        #no criteria
        if len(param)==0:
            df = df[col]
        else:
            df = self.mtd.evalCriteria(df,param,col)        
        df1 = pandas.merge(tablein,df,how='inner')
                
        return df1  
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_zack()
    obj.test()