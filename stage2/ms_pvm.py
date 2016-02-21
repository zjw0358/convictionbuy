'''
marketscan module
- download stock px,p/s,marketcap,avgvol,peg,dividend from Yahoo Finance website
- filter by the above columns

use case:
    default = no download 
run marketscan -g "ms_pvm&avgvol>1000000&peg<2"
run marketscan -g "ms_pvm&download"

http://finance.yahoo.com/d/quotes.csv?s=JNJ&f=sp5j1a2l1r5yq
'''

import datetime
import urllib2
import csv
import pandas
#import re
import marketdata
import ms_config
import ms_paramparser
import sys
from collections import OrderedDict
from ind_base_nopx import BaseIndNoPx



class ms_pvm(BaseIndNoPx):
    def __init__(self):
        # TODO move to common module
        pandas.set_option('display.expand_frame_repr', False) #expand wide dataframe
        self.columns = ['symbol','pricesale','marketcap','avgvol','px','peg','dividend','divdate']
        self.colcode = "&f=sp5j1a2l1r5yq"
        self.cfg = ms_config.MsDataCfg("")
        self.pvmfile = self.cfg.getDataConfig("pvm")
        #self.cachefolder = self.cfg.getDataConfig("folder")
        self.hasCachedDF = False
        self.today = datetime.datetime.now()
        BaseIndNoPx.__init__(self)
        #self.mtd = marketdata.MarketData()
        return        

#------------------------------------------------------------------------
    def _adjustDividendDate(self,oridatestr):
        try:
            oridate = datetime.datetime.strptime(oridatestr,'%m/%d/%Y')
        except:        
            return oridatestr
            
        if (oridate < self.today):
            newdate = oridate + datetime.timedelta(days=90)
            return newdate.strftime("%m/%d/%Y")
        else:
            return oridatestr
        pass
        
    def _loadData(self,fileName):
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
        divdate = 7
        for row in reader:
            if idx==0:
                idx += 1
                continue
            for rowid, item in enumerate(row):            
                lst = allLst[self.columns[rowid]]
                '''
                if rowid!=0:
                    item=item.replace(" ","")
                    if item=="":
                        item=0
                    #print item
                    lst.append(item)
                else:                
                    lst.append(item)
                '''
                if (rowid==divdate):
                    item = self._adjustDividendDate(item)
                    lst.append(item)
                else:
                    lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=self.columns)
        return table
    
    # strategy process  
    def process(self,tablein):        
        ticklist = tablein['symbol']
        param = OrderedDict()
        
        #replace keyword in parameter
        for pa in self.param:
            param[pa]=""
        
        #print "ms_pvm parameter=",param        
        col = ['symbol']            

        if (not self.hasCachedDF):            
            df = self._loadData(self.pvmfile)             
            self.cacheDF = df
            self.hasCachedDF = True
        else:
            df = self.cacheDF
            pass

        #no criteria, select all columns
        if len(param)==0:
            #df = df[col]
            cols = df.columns.values
            pass
        else:
            df,cols = self.mtd.evalCriteria(df,param,col)
            
            
        
                          
        
        #if df.empty:
        #    print "error happened, unable to process ms_pvm, return original table"
        #    return tablein
        
        df1 = pandas.merge(tablein,df,how='inner')
        return df1,cols
    
    
    def download(self,argstr=""):
        if (argstr==""):
            args = sys.argv[1:]
        else:
            args= argstr.split()
        self.params = ms_paramparser.ms_paramparser()
        self.params.parseOption(args)
        df = self.params.getSymbolDf()
        ticklist = df['symbol']
        self._downloadData(ticklist)
    
    #data from yahoo,limit=200               
    def _downloadData(self,ticklist):
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
                #print idx,symstr
                if idx%limit==0:                    
                    url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                    #print url
                    response = urllib2.urlopen(url)
                    cr = csv.reader(response)
                    for row in cr:
                        #print row
                        for rowid,item in enumerate(row):
                            dataLst[rowid].append(item)
                            '''
                            if rowid==0:
                                dataLst[rowid].append(item) 
                            else:
                                dataLst[rowid].append(self.mtd.tofloat(item))
                            '''
                        #retidx +=1
                    symstr=""
                    
            if symstr!="":                
                url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                #print "last get",url
                response = urllib2.urlopen(url)
                cr = csv.reader(response)
                for row in cr:
                    for rowid,item in enumerate(row):
                        dataLst[rowid].append(item)
                        '''
                        if rowid==0:
                            dataLst[rowid].append(item)
                        else:
                            dataLst[rowid].append(self.mtd.tofloat(item))
                        '''
            table=pandas.DataFrame(dataDct,columns=self.columns)
            table.to_csv(self.pvmfile,sep=',',index=False)
            print "successfully save pvm file to",self.pvmfile
        except:
            print "System/Network Error when retrieving data, return..."
        return table    
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_pvm()
    obj.download()    
    