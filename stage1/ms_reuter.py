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
#from collections import OrderedDict

class ms_reuter:
    def __init__(self):
        self.reuter = reuterfunda.ReuterFunda()
        self.reuterFile = "./msdata_reuter_2015-04-19.csv"
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
    '''
    def setupParam(self,param):
        param1 = OrderedDict()
        self.sgy = 0
        for pn in param:
            if pn=='sgy':
                sgystr = param['sgy']
                if sgystr == "eracc":
                    self.sgy = 1
                elif sgystr == "eraccyoy":
                    self.sgy = 2
            else:
                param1[pn]=""
        return param1
    '''
    '''    
    def process(self,tablein,param):
        param = self.setupParam(param)
        ticklist = tablein['symbol']
        col = self.reuter.colbase
        if self.sgy == 1:
            col = col + ['epsq1e','epsqtr0','epsqtr-1','epsqtr-2','epsqtr-3','epsqtr-4']
        elif self.sgy == 2:
            col = col + ['epsq1e','epsqtr0','epsqtr-1','epsqtr-2','epsqtr-3','epsqtr-4','epsqtr-5','epsqtr-6']
            
        df = self.loadData(self.reuterFile)
        
        #no criteria
        if len(param)==0:
            df = df[col]
        else:
            df = self.mtd.evalCriteria(df,param,col)        
        df1 = pandas.merge(tablein,df,how='inner')
        
        #more strategy
        # TODO delete
        if self.sgy==1:
            #eracc
            print "screen = earning acceration QoQ"
            df1 = self.eracc(df1)
        elif self.sgy==2:
            print "screen = earning acceration YoY"
            df1 = self.eracc2(df1)
        return df1
    '''
    def process(self,tablein,param):
        #param = self.setupParam(param)
        ticklist = tablein['symbol']
        macro = {
            "$eracc1":"epsqtr0/epsqtr-1>epsqtr-1/epsqtr-2&epsqtr-1/epsqtr-2>epsqtr-2/epsqtr-3&epsq1e/epsqtr0>epsqtr0/epsqtr-1",
            "$eracc2":"epsq1e/epsqtr-3>epsqtr0/epsqtr-4&epsqtr0/epsqtr-4>epsqtr-1/epsqtr-5&epsqtr-1/epsqtr-5>epsqtr-2/epsqtr-6",
            "$eps":"epsqtr0&epsqtr-1&epsqtr-2&epsqtr-3&epsqtr-4&epsqtr-5&epsqtr-6&epsqtr-7&epsqtr-8&epsqtr-9"
        }
        #replace keyword in parameter
        for ma in macro:
            if ma in param:
                del param[ma]
                crlst = macro[ma].split("&")
                for cr in crlst:
                    param[cr]=""

        print "ms_reuter parameter=",param
        
        col = ['symbol']            
        df = self.loadData(self.reuterFile)
        
        #no criteria
        if len(param)==0:
            df = df[col]
        else:
            df = self.mtd.evalCriteria(df,param,col)        
        df1 = pandas.merge(tablein,df,how='inner')
                
        return df1
        
    #zack strategy earning acceleration p43, earning improve QoQ
    # epsq increase for constructive 3 qtr
    '''
    def eracc(self,df):
        f0 = df[ (df['epsqtr0']/df['epsqtr-1'] > df['epsqtr-1']/df['epsqtr-2']) & \
                (df['epsqtr-1']/df['epsqtr-2'] > df['epsqtr-2']/df['epsqtr-3']) & \
                (df['epsq1e']/df['epsqtr0'] > df['epsqtr0']/df['epsqtr-1'])]
        return f0

    #zack strategy earning acceleration p43, earning improve QoQ        
    def eracc2(self,df):
        f0 = df[ (df['epsq1e']/df['epsqtr-3'] > df['epsqtr0']/df['epsqtr-4']) & \
                (df['epsqtr0']/df['epsqtr-4'] > df['epsqtr-1']/df['epsqtr-5']) & \
                (df['epsqtr-1']/df['epsqtr-5'] > df['epsqtr-2']/df['epsqtr-6'])
             ]
        return f0
    '''     
    def test(self):
        ticklist = ['LLY','BMY','ABBV','GILD','PFE','MRK','JNJ','GSK']
        self.process(ticklist,"")
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_reuter()
    obj.test()