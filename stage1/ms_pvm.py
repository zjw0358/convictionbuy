'''
marketscan module
- download stock p/s,marketcap,avgvol
- filter by pricesale,marketcap,avgvol,px

use case:    
run marketscan -g "ms_pvm&avgvol>1000000&download=1"

'''
import datetime
import urllib2
import csv
import pandas
import re
import marketdata

# marketscan module price/volume/marketcap
class ms_pvm:
    def __init__(self):
        self.columns = ['symbol','pricesale','marketcap','avgvol','px']
        self.colcode = "&f=sp5j1a2l1"
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
            for idx, symbol in enumerate(ticklist):
                symstr += symbol
                if idx<(lenlist-1) and (idx%limit!=0):
                    symstr +="+"
                    
                if idx%limit==0:
                    print idx,symstr
                    url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                    response = urllib2.urlopen(url)
                    cr = csv.reader(response)
                    for row in cr:
                        print row
                        for rowid,item in enumerate(row):
                            if rowid==0:
                                dataLst[rowid].append(item) 
                            else:
                                dataLst[rowid].append(self.format(item))
                            
                        #retidx +=1
                    symstr=""
                    
            if symstr!="":
                print "last get",symstr
                url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                response = urllib2.urlopen(url)
                cr = csv.reader(response)
                for row in cr:
                    for rowid,item in enumerate(row):
                        if rowid==0:
                            dataLst[rowid].append(item)
                        else:
                            dataLst[rowid].append(self.format(item))
                
            table=pandas.DataFrame(dataDct,columns=self.columns)
            table.to_csv(self.outputFileName,sep=',',index=False)
        except:
            print "System/Network Error when retrieving data, return..."
        return table
    
    def format(selv,item):
        #print item
        if item=="N/A":
            return "0"
        elif item[-1]=="K":
            return float(item.replace("K",""))*1000
        elif item[-1]=="M":
            return float(item.replace("M",""))*1000000
        elif item[-1]=="B":
            return float(item.replace("B",""))*1000000000
        elif item[-1]=="T":
            return float(item.replace("T",""))*1000000000000
        else:
            return float(item)

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
     
    # no need real price data
    def needPriceData(self):
        return False
        
    #main routine       
    def process(self,tablein,param):
        download = 1  #default = download
        ticklist = tablein['symbol']
        #extract 'download' option
        param1={}
        for op in param:
            if op == 'download':
                download = int(param['download'])
            else:
                param1[op]=""
                
        if (download == 1):
            df = self.downloadData(ticklist)            
        else:
            df = self.loadData(self.outputFileName)                    

        col = ['symbol']
        df = self.mtd.evalCriteria(df,param1,col)        
        #df1 = df[df['symbol'].isin(ticklist)]
        #merge df1 & tablein
        df1 = pandas.merge(tablein,df,how='inner')
        return df1

        

    '''
    def process(self,ticklist,param):
        self.download = 1  #default = download


        self.criteria = []
        self.ticklist = ticklist
        for op in param:
            if op == 'download':
                self.download = int(param['download'])
            else:
                self.criteria.append(op)
        
        # check criteria
        if not self.criteria:
            print "criteria is empty,...return original ticklist"
            return ticklist
            
        if (self.download == 1):
            df = self.downloadData(ticklist)            
        else:
            df = self.loadData(self.outputFileName)
            
        # filter by dynamic criteria string
        crstr = ""
        pattern = "([\w]+)([><])([\d]+)"

        for cr in self.criteria:
            an = re.match(pattern,cr)            
            if an!=None:
                cr0 = "(df['%s']%s%s) & " % (an.group(1),an.group(2),an.group(3))
                crstr += cr0
         
        crstr += "(1)"
        print "criteria = ", crstr
        return df[eval(crstr)]['symbol']  
    '''    
       
    