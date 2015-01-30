import pandas.io.data as web
import pandas
import datetime
import urllib2
import csv
import getopt
import sys
import marketdata
'''
historical price
http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv

using yahoo finance api
http://www.jarloo.com/yahoo_finance/
http://finance.yahoo.com/d/quotes.csv?s=msft&f=sp5j1a2l1
'''

class FundaData:
    def __init__(self):       
        '''
        self.startdate = ""
        self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
        startday = datetime.date.today() - datetime.timedelta(days=365)
        self.startdate = startday.strftime("%Y-%m-%d")
        '''
        self.columns = ['symbol','pricesale','marketcap','avgdailyvol','px']
        self.colcode = "&f=sp5j1a2l1"
        self.sufname = "fundaupdate_"
        self.outputpath = "../data/"
        self.mkt = marketdata.MarketData()

    def setDateRange(self,enddatestr):
        if enddatestr=="":
            enddate = datetime.datetime.now()
        else:
            enddate = datetime.datetime.strptime(enddatestr,'%Y-%m-%d')
            
        startday = enddate - datetime.timedelta(days=365)
        self.enddate = enddatestr
        self.startdate = startday.strftime("%Y-%m-%d")
            
    def getPerf(self,symbol, param, enddatestr=""):
        ret = {}
        self.setDateRange(enddatestr)
        try:
            ohlc = web.get_data_yahoo(symbol, self.startdate, self.enddate)
        except:
            # IO error
            print "System/Network Error when retrieving ",symbol," skip it"
            return ret
        # calculate perf
        # print symbol
        px = ohlc['Adj Close']
        p1d = 0
        p4w = 0
        p12w = 0
        p24w = 0
        pmax = 0
        plen = len(px)
        if plen >= 2:
            p1d = round((px[-1]/px[-2] - 1)*100,2)    
        if plen >= 4*7:
            p4w = round((px[-1]/px[-4*7] - 1)*100,2)
        if plen >= 12*7:
            p12w = round((px[-1]/px[-12*7] - 1)*100,2)
        if plen >= 24*7:
            p24w = round((px[-1]/px[-24*7] - 1)*100,2)
        if len(px) >= 1*7:
            p1w = round((px[-1]/px[-1*7] - 1)*100,2)

        pmax = round((px[-1]/px[0] - 1) * 100,2)

        if 'vol20' in param:
            sma20vol = pandas.stats.moments.rolling_mean(ohlc['Volume'],20)
            ret['vol20'] = sma20vol[-1]
            
        if 'vol' in param:            
            ret['vol'] = ohlc['Volume'][-1]
            
        if 'px' in param:            
            ret['px'] = ohlc['Adj Close'][-1]
                      
        if 'ma10' in param:
            sma10s = pandas.stats.moments.rolling_mean(px,10)
            ret['ma10'] = round(sma10s[-1],2)
        
        if 'ma50' in param:            
            sma50s = pandas.stats.moments.rolling_mean(px,50)            
            ret['ma50'] = round(sma50s[-1],2)
            
        if 'ma200' in param:                        
            sma200s = pandas.stats.moments.rolling_mean(px,200)
            ret['ma200'] = round(sma200s[-1],2) 

        ret['p1d'] = p1d
        ret['p1w'] = p1w  
        ret['p4w'] = p4w
        ret['p12w'] = p12w
        ret['p24w'] = p24w
        return ret
        
    #data from yahoo,limit=200               
    def getFundData(self, ticklist):
        symstr = ""
        limit = 199 #yahoo limit is 200
        lenlist = len(ticklist)
        #stockps = []
        dataDct = {}
        dataLst = []
        for idx,col in enumerate(self.columns):
            lst=[]
            dataDct[col]=lst
            dataLst.append(lst)
        
        #retidx= 0 
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
            
    def usage(self):
        print "program -f symbollist.txt"

   
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:", ["filename"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.fileName = arg
                
        if (self.fileName == ""):
            self.usage()
            sys.exit()
            
        print "symbolfile=",self.fileName
        return
        
    #zack symbol list csv    
    def updateFundata(self):
        df = self.mkt.loadSymbolLstFile(self.fileName)
        ticklist = df[df['rank']>0]['symbol']
        table = self.getFundData(ticklist)
        outputfn = self.outputpath + self.sufname + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'       
        table.to_csv(outputfn,sep=',',index=False)
        
        '''
        # symbol,rank
        fp = open(self.fileName,'r',-1)
        ticklist=[]
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx +=1
                continue
            ticklist.append(row[0]) #symbol
            idx += 1
        fp.close()      # closing
        table = self.getFundData(ticklist)
        outputfn = self.outputpath + self.sufname + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'       
        table.to_csv(outputfn,sep=',',index=False)
        '''
    #fundata csv file
    def loadFundaCsv(self,fileName):
        print "Loading fundata csv file..."         
        allLst = {}
        for key in self.columns:
            lst = []
            allLst[key] = lst
                
        table = pandas.DataFrame(allLst,columns=self.columns)
        
        fp = open(fileName,'r',-1)
        
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
        
                
    def process(self):
        self.parseOption()
        self.updateFundata()
        return
        
if __name__ == "__main__":
    obj = FundaData()
    obj.process()