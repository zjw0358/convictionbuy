'''
marketscan module
- filter by reuter fundamental data

use case:    
run marketscan -g "ms_reuter" -t "LLY,NVS,JNJ,BMY,GILD,MRK,PFE,IBB,ABBV,ANT,BIIB,AMGN,AZN"

'''
import reuterfunda
import pandas
import datetime
import re
import marketdata
from collections import OrderedDict

class ms_reuter:
    def __init__(self):
        self.reuter = reuterfunda.ReuterFunda()
        self.reuterFile = "./msdata_reuter_2015-01-27.csv"
        self.mtd = marketdata.MarketData()
        return        

    def loadData(self,fileName):
        df = self.reuter.loadReuterCsvFile(self.reuterFile)
        return df
        
    def parseParam(self,param):
        return
    

    # no need real price data
    def needPriceData(self):
        return False
    
    def setupParam(self,param):
        param1 = {}
        self.sgy = 0
        for pn in param:
            if pn=='sgy':
                sgystr = param['sgy']
                if sgystr == "eracc":
                    self.sgy = 1
            else:
                param1[pn]=""
        return param1
        
    def process(self,tablein,param):
        param = self.setupParam(param)
        ticklist = tablein['symbol']
        col = self.reuter.colbase
        if self.sgy==1:
            col = col + ['epsqtr0','epsqtr-1','epsqtr-2','epsqtr-3','epsqtr-4']
            
        df = self.loadData(self.reuterFile)
        
        #no criteria
        if len(param)==0:
            df = df[col]
        else:
            df = self.mtd.evalCriteria(df,param,col)        
        df1 = pandas.merge(tablein,df,how='inner')
        
        #more strategy
        if self.sgy==1:
            #eracc
            print "screen = earning acceration"
            df1 = self.eracc(df1)
        
        return df1
        
    #zack strategy earning acceleration p43  
    def eracc(self,df):
          # epsq increase for constructive 3 qtr,marketcap> 2B,avgvol > 500k
        f0 = df[ (df['epsqtr0']/df['epsqtr-1'] > df['epsqtr-1']/df['epsqtr-2']) & \
                (df['epsqtr-1']/df['epsqtr-2'] > df['epsqtr-2']/df['epsqtr-3']) ]
        return f0
        
    def test(self):
        ticklist = ['LLY','BMY','ABBV','GILD','PFE','MRK','JNJ','GSK']
        self.process(ticklist,"")
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_reuter()
    obj.test()