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
from ms_base_npx import MsBaseNPx


class ms_pvm(MsBaseNPx):
    def __init__(self):
        self.columns = ['symbol','pricesale','marketcap','avgvol','px','peg','dividend']
        self.colcode = "&f=sp5j1a2l1r5y"
        self.outputFileName = "./msdata_pvm.csv"
        self.mtd = marketdata.MarketData()
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
            table.to_csv(self.outputFileName,sep=',',index=False)
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
                    lst.append(float(item))
                else:
                    lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=self.columns)
        return table
     
    ''' # no need real price data
    def needPriceData(self):
        return False
    '''
        
    #main routine       
    def process(self,tablein,param):
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
            df = self.loadData(self.outputFileName)                    

        if df.empty:
            print "error happened, unable to process ms_pvm, return original table"
            return tablein
            
        col = ['symbol']
        df = self.mtd.evalCriteria(df,param1,col)        
        #df1 = df[df['symbol'].isin(ticklist)]
        #merge df1 & tablein
        df1 = pandas.merge(tablein,df,how='inner')
        return df1
       
    
    