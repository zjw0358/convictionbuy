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
        self.reuterFile = "./msdata_reuter_2015-05-13.csv"
        self.mtd = marketdata.MarketData()
        return        

    def loadData(self,fileName):
        df = self.reuter.loadReuterCsvFile(self.reuterFile)
        return df
        
    def parseParam(self,param):
        return
    
    def usage(self):
        return "ms_reuter: $eracc1, $eracc2,$eps"


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
    def epsyoy(self,df):
        df['q0gr'] = df['epsqtr0']/df['epsqtr-4']
        df['q1gr'] = df['epsqtr-1']/df['epsqtr-5']
        df['q2gr'] = df['epsqtr-2']/df['epsqtr-6']
        df['q3gr'] = df['epsqtr-3']/df['epsqtr-7']
        df['q4gr'] = df['epsqtr-4']/df['epsqtr-8']
        df['q5gr'] = df['epsqtr-5']/df['epsqtr-9']
        '''
        df = df.drop('epsqtr0', 1)
        df = df.drop('epsqtr-1', 1)
        df = df.drop('epsqtr-2', 1)
        df = df.drop('epsqtr-3', 1)
        df = df.drop('epsqtr-4', 1)
        df = df.drop('epsqtr-5', 1)                
        df = df.drop('epsqtr-6', 1)
        df = df.drop('epsqtr-7', 1)
        df = df.drop('epsqtr-8', 1)
        df = df.drop('epsqtr-9', 1)
        '''
        df=df[['symbol','q0gr','q1gr','q2gr','q3gr','q4gr']]
        #>/epsqtr-5&epsqtr-1/epsqtr-5>epsqtr-2/epsqtr-6&epsqtr-2/epsqtr-6>epsqtr-3/epsqtr-7
        
        
        return df
        
    def process(self,tablein,param0):
        #"$eracc2":"epsq1e/epsqtr-3>epsqtr0/epsqtr-4&epsqtr0/epsqtr-4>epsqtr-1/epsqtr-5&epsqtr-1/epsqtr-5>epsqtr-2/epsqtr-6",
        ticklist = tablein['symbol']
        param = OrderedDict()
        macro = {
            "$eracc1":"epsqtr0/epsqtr-1>epsqtr-1/epsqtr-2&epsqtr-1/epsqtr-2>epsqtr-2/epsqtr-3&epsq1e/epsqtr0>epsqtr0/epsqtr-1",
            "$eracc2":"epsqtr0&epsqtr-1&epsqtr-2&epsqtr-3&epsqtr-4&epsqtr-5&epsqtr-6&epsqtr-7&epsqtr0/epsqtr-4>epsqtr-1/epsqtr-5&epsqtr-1/epsqtr-5>epsqtr-2/epsqtr-6&epsqtr-2/epsqtr-6>epsqtr-3/epsqtr-7",
            "$eps":"epsqtr0&epsqtr-1&epsqtr-2&epsqtr-3&epsqtr-4&epsqtr-5&epsqtr-6&epsqtr-7&epsqtr-8&epsqtr-9",
            "$fa1":"cppettm&sectorpettm&cppsttm&cppbmrq&cppcfttm&cpquira&cpcurra&cpdebt2equity&cproe&cproa&cproi&divyield&payoutratio&cpgm&cpom&cpnm&cpbeta",
            "$cvs":"cppcfttm<=10&cppettm<=20&cppsttm<=1&cppbmrq<=2",
            #cvs - combine valuation screen p50 (ps, pcf, pb, peg)
            "$epsyoy":"epsqtr0&epsqtr-1&epsqtr-2&epsqtr-3&epsqtr-4&epsqtr-5&epsqtr-6&epsqtr-7&epsqtr-8&epsqtr-9"
        }
        #debt /ratio?
        #replace keyword in parameter
        for pa in param0:
            if pa in macro:
                crlst = macro[pa].split("&")                            
                for cr in crlst:
                    param[cr]=""
            else:
                param[pa]=""
                

        print "ms_reuter parameter=",param
        
        col = ['symbol']            
        df = self.loadData(self.reuterFile)
        
        #no criteria
        if len(param)==0:
            df = df[col]
        else:
            df = self.mtd.evalCriteria(df,param,col)
            
        #post process
        if "$epsyoy" in param0:
            df = self.epsyoy(df)
        #print df    
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