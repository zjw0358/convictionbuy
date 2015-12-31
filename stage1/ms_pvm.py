'''
marketscan module
- download stock px,p/s,marketcap,avgvol,peg,dividend from Yahoo Finance website
- filter by the above columns

use case:
    default = no download 
run marketscan -g "ms_pvm&avgvol>1000000&peg<2"
run marketscan -g "ms_pvm&download"
'''

import datetime
import urllib2
import csv
import pandas
import re
import marketdata
import ms_config
import ms_paramparser
import sys
from ind_base_nopx import BaseIndNoPx
#from ms_base_npx import MsBaseNPx


class ms_pvm(BaseIndNoPx):
    def __init__(self):
        self.columns = ['symbol','pricesale','marketcap','avgvol','px','peg','dividend','divdate']
        self.colcode = "&f=sp5j1a2l1r5yq"
        #self.outputFileName = "./msdata_pvm.csv"
        self.cfg = ms_config.MsDataCfg("")
        self.pvmfile = self.cfg.getDataConfig("pvm")
        self.cachefolder = self.cfg.getDataConfig("folder")
        BaseIndNoPx.__init__(self)
        #self.mtd = marketdata.MarketData()
        return        

    #data from yahoo,limit=200               
    def downloadData(self,ticklist):
        symstr = ""
        limit = 199 #yahoo limit is 200
        lenlist = len(ticklist)

        dataDct = {}
        dataLst = []
        for idx,col in enumerate(self.columns):
            lst=[]
            dataDct[col]=lst
            dataLst.append(lst)
            
        table=pandas.DataFrame()
        try:
            print "downloading yahoo data..."
            for idx, symbol in enumerate(ticklist):
                symstr += symbol
                if idx<(lenlist-1) and (idx%limit!=0):
                    symstr +="+"
                    
                if idx%limit==0:
                    #print idx,symstr
                    url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                    response = urllib2.urlopen(url)
                    cr = csv.reader(response)
                    for row in cr:
                        #print row
                        for rowid,item in enumerate(row):
                            if rowid==0:
                                dataLst[rowid].append(item) 
                            else:
                                dataLst[rowid].append(self.mtd.tofloat(item))
                            
                        #retidx +=1
                    symstr=""
                    
            if symstr!="":
                #print "last get",symstr
                url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                response = urllib2.urlopen(url)
                cr = csv.reader(response)
                for row in cr:
                    for rowid,item in enumerate(row):
                        if rowid==0:
                            dataLst[rowid].append(item)
                        else:
                            dataLst[rowid].append(self.mtd.tofloat(item))
                
            table=pandas.DataFrame(dataDct,columns=self.columns)
            table.to_csv(self.pvmfile,sep=',',index=False)
        except:
            print "System/Network Error when retrieving data, return..."
        return table

    def loadData(self,fileName):
        print "Loading PVM csv file..."         
        allLst = {}
        for key in self.columns:
            lst = []
            allLst[key] = lst
                
        table = pandas.DataFrame(allLst,columns=self.columns)
        
        try:
            fp = open(fileName,'r',-1)
        except:
            print "File not exist, try downloading..."
            return self.downloadData(self.ticklist)    
            
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            for rowid, item in enumerate(row):            
                lst = allLst[self.columns[rowid]]
                if rowid!=0:
                    item=item.replace(" ","")
                    if item=="":
                        item=0
                    #print item
                    lst.append(item)
                else:
                    lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=self.columns)
        return table
     
        
    #main routine       
    def process(self,tablein,param):
        self.setupParam(param)
        download = 0  #default = download
        ticklist = tablein['symbol']
        #extract 'download' option
        param1={}
        for op in param:
            if op == 'download':
                download = 1
            else:
                param1[op]=""
                
        if (download == 1):
            df = self.downloadData(ticklist)            
        else:
            df = self.loadData(self.pvmfile)                    

        if df.empty:
            print "error happened, unable to process ms_pvm, return original table"
            return tablein
            
        col = ['symbol'] # df.columns.values  #
        # the output would be symbol + column in criteria
        df,cols = self.mtd.evalCriteria(df,param1,col)        
        #df1 = df[df['symbol'].isin(ticklist)]
        #merge df1 & tablein
        df1 = pandas.merge(tablein,df,how='inner')
        return df1

    # move to marketdata later   
    def main(self):
        params = ms_paramparser.ms_paramparser()
        params.parseOption(sys.argv[1:])
        if (params.tickdf.empty):
            df = self.mtd.loadSymbolLstFile(params.symbolLstFile)
            df = self.mtd.getSymbolByPid(df,params.pid)[['symbol']]
        else:
            df = params.tickdf
        if (not 'ms_pvm' in params.sgyparam):
            args = dict((k,'') for k in self.columns)
        else:
            args = params.sgyparam['ms_pvm']
        df = self.process(df,args)
        print df
        pass  
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_pvm()
    obj.main()    
    