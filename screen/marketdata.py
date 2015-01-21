import getopt
import datetime
import sys
import pandas.io.data as web
import pandas
import fundata
import csv

'''
http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv

'''
class MarketData:
    def __init__(self):
        self.columns = ['symbol','5d','10d','20d', '50d', '100d','200d','max','px', \
                        'sma10','sma50','sma200','sma10%','sma50%','sma200%']
        self.perftable = pandas.DataFrame(columns=self.columns) 
        self.outputpath = "../result/"
        self.option = ""
        self.dow30fn = "../data/dow30.txt"
        self.funda = fundata.FundaData()
        #pandas.options.display.float_format = '{:,.2f}%'.format
        self.spdretf = {'Consumer Discretionary':'XLY','Consumer Staples':'XLP','Energy':'XLE',\
                    'Financials':'XLF','Health Care':'XLV','Industrials':'XLI','Materials':'XLB',\
                    'Technology':'XLK','Utilities':'XLU'}
                    
        self.sectormapping = {'Consumer Discretionary':'Consumer Services','Consumer Staples':'Consumer Non-Durables',\
                'Energy':'Energy','Financials':'Finance','Health Care':'Health Care','Technology':'Technology',\
                'Industrials':'Basic Industries','Industrials':'Transportation','Industrials':'Capital Goods',\
                'Materials':'Basic Industries','Capital Goods':'xlb','Health Care':'xlv','Consumer Services':'xly', \
                'Utilities':'Public Utilities'}              

        return
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' -s 2010-01-01 -e 2014-12-30"
  
    # google style portfolio file
    def loadPortfolioFile(self,fileName):
        #print "open file:",fileName
        fp = open(fileName,'r',-1)
        pf = fp.read()
        stocklist=[]
        #print pf
        for item in pf.split():            
            market,symbol = item.split(':')
            print symbol
            stocklist.append(symbol)
                    
        fp.close()
        return stocklist
        
    def parseOption(self):
        self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
        startday = datetime.date.today() - datetime.timedelta(days=365)
        self.startdate = startday.strftime("%Y-%m-%d")
        self.ticklist=[]

        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:s:e:", ["filename", "ticklist", "startdate","enddate"])
        except getopt.GetoptError:
            print "parse option error"
            return False

        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.ticklist = self.loadPortfolioFile(arg)
            elif opt in ("-t", "--ticklist"):
                newstr = arg.replace("'", "")                
                self.ticklist = newstr.split()
            elif opt in ("-s", "--startdate"):
                self.startdate = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
                
        if (not self.ticklist):
            self.option = "marketdata"
        
        #self.ticklist.append("^GSPC")
        
    def runPerfCompare(self):
        all_data = {}
        for ticker in self.ticklist:
            # retrieve data
            try:
                all_data[ticker] = web.get_data_yahoo(ticker, self.startdate, self.enddate)
            except:
                # IO error
                print "System/Network Error when retrieving ",ticker," skip it"
                continue
                
            # calculate perf
            px = all_data[ticker]['Adj Close']
            p5d = ""
            p10d = ""
            p20d = ""
            p50d = ""
            p100d = ""
            p200d = ""
            pmax = ""
            if len(px) >= 5:
                p5d = str(round((px[-1]/px[-5]-1)*100,2))+"%"
            if len(px) >= 10:
                p10d = str(round((px[-1]/px[-10]-1)*100,2))+"%"
            if len(px) >= 20:
                p20d = str(round((px[-1]/px[-20]-1)*100,2))+"%"
            if len(px) >= 50:
                p50d = str(round((px[-1]/px[-50]-1)*100,2))+"%"
            if len(px) >= 100:
                p100d = str(round((px[-1]/px[-100]-1)*100,2))+"%"
            if len(px) >= 200:
                p200d = str(round((px[-1]/px[-200]-1)*100,2))+"%"                
            pmax = str(round((px[-1]/px[0] - 1) * 100,2))+"%"
            sma10s = pandas.stats.moments.rolling_mean(px,10)
            sma50s = pandas.stats.moments.rolling_mean(px,50)
            sma200s = pandas.stats.moments.rolling_mean(px,200)
            sma10 = str(sma10s[-1])
            sma50 = str(sma50s[-1])
            sma200 = str(sma200s[-1])
            sma10p = str(round((px[-1]/sma10s[-1]-1)*100,2))+"%"
            sma50p = str(round((px[-1]/sma50s[-1]-1)*100,2))+"%"
            sma200p = str(round((px[-1]/sma200s[-1]-1)*100,2))+"%"            
            d0 = {'symbol':ticker,'5d':p5d,'10d':p10d,'20d':p20d,'50d':p50d,'100d':p100d,'200d':p200d,\
                     'max':pmax,'px':px[-1],'sma10':sma10,'sma50':sma50,'sma200':sma200,'sma10%':sma10p,\
                     'sma50%':sma50p,'sma200%':sma200p }
            print d0     
            self.perftable.loc[len(self.perftable)+1]=d0
        return

    
    def makeReport(self):
        sortTable = self.perftable.sort_index(by='5d',ascending=False)
        #filename = self.outputpath + 'perfscreen_' + time.strftime('%Y-%m-%d.csv',time.localtime(time.time()))
        filename = self.outputpath + 'perfscreen_' + self.enddate + '_' + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        try:
            sortTable.to_csv(filename,sep=',')
        except:
            print "exception when write to csv ",filename
        
        print "================================================================"
        print "Performance Screen  results:"
        print sortTable
        print "================================================================" 
  
    def loadSymbolLstFile(self,fileName):
        # symbol,pricesale
        fp = open(fileName,'r',-1)
        stockLst = []
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            print row[0]
            if row[0]!="":
                stockLst.append(row[0])
            idx += 1
        fp.close()      # closing
        return stockLst
        
    def procMarketData(self):
        # dow30
        lst = self.loadSymbolLstFile(self.dow30fn)
        dow30Dct = {}
        for symbol in lst:
            dow30Dct[symbol]=symbol
        self.getMarketData(dow30Dct)    
        self.getMarketData(self.spdretf)            
        
        return
        
    def getMarketData(self,tickLst):
        param = {'vol20':0,'ma':0,'p1w':1}        
        nameLst = []
        symbolLst = []
        p1w = []
        p4w = []
        p12w = []
        p24w = []
        for name in tickLst:
            tick = tickLst[name]
            ret = self.funda.getPerf(tick,param)
            nameLst.append(name)
            symbolLst.append(tick)
            p1w.append(ret['p1w'])
            p4w.append(ret['p4w'])
            p12w.append(ret['p12w'])
            p24w.append(ret['p24w'])
            
        table = pandas.DataFrame({'name':nameLst,'symbol':symbolLst,\
            '1week_perf':p1w,'4week_perf':p4w,'12week_perf':p12w,'24week_perf':p24w},\
            columns=['name','symbol','1week_perf','4week_perf','12week_perf','24week_perf'])
            
        print table.sort_index(by=['24week_perf','12week_perf','4week_perf','1week_perf'],\
            ascending=[False,False,False,False])

        
    def process(self):
        self.parseOption()
        if self.option != "marketdata":
            self.runPerfCompare()
            self.makeReport()
        else:
            self.procMarketData()
        
if __name__ == "__main__":
    obj = MarketData()
    obj.process()
    #process(sys.argv[1:],None)