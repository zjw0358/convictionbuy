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
    '''
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
    '''    
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
        #symbol,rank,name,sector,industry,pid
        fp = open(fileName,'r',-1)
        #stockLst = []
        symbolLst = []
        rankLst = []
        nameLst = []
        sectorLst = []
        industryLst = []
        pidLst = []
        exgLst = []
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            symbolLst.append(row[0])
            rankLst.append(int(row[1]))
            nameLst.append(row[2])
            sectorLst.append(row[3])
            industryLst.append(row[4])
            pidLst.append(row[5])
            exgLst.append(row[6])
            idx += 1
        fp.close()      # closing
        table = pandas.DataFrame({'symbol':symbolLst,'rank':rankLst,'name':nameLst,\
            'sector':sectorLst,'industry':industryLst,'pid':pidLst,'exg':exgLst},\
            columns=['symbol','rank','name','sector','industry','pid','exg'])
        return table


        
    def procMarketData(self):
        '''
        # dow30
        lst = self.loadSymbolLstFile(self.dow30fn)
        dow30Dct = {}
        for symbol in lst:
            dow30Dct[symbol]=symbol
        '''
        df = self.loadSymbolLstFile("./marketdata.csv")
        #criteria setting
        criterion = df['pid'].map(lambda x: (int(x)&1==1))
        dow30Lst = df[criterion]['symbol']
        dow30Dct = {}
        for symbol in dow30Lst:
            dow30Dct[symbol]=symbol    
        param = {'vol20':0,'vol':0,'ma10':0,'ma50':0,'ma200':0,'px':0}        
        #print dow30Dct
        self.getMarketData(dow30Dct,param)
        
        #dow30Lst = df[(df['pid']==3)]
        #print dow30Lst
        #self.getMarketData(dow30Dct)
        #self.getMarketData(self.spdretf)            
        
        return
        
    def getMarketData(self,tickLst,param):
        nameLst = []
        symbolLst = []
        p1d = []
        p1w = []
        p4w = []
        p12w = []
        p24w = []
        ma10 = []
        ma50 = []
        ma200 = []
        vol20 = []
        voltd = []
        px = []
        for name in tickLst:
            tick = tickLst[name]
            ret = self.funda.getPerf(tick,param)
            nameLst.append(name)
            symbolLst.append(tick)
            p1d.append(ret['p1d'])
            p1w.append(ret['p1w'])
            p4w.append(ret['p4w'])
            p12w.append(ret['p12w'])
            p24w.append(ret['p24w'])
            if 'ma10' in param:
                ma10.append(ret['ma10'])
            if 'ma50' in param:
                ma50.append(ret['ma50'])
            if 'ma200' in param:
                ma200.append(ret['ma200'])
            if 'vol20' in param:
                vol20.append(ret['vol20'])
            if 'vol' in param:
                voltd.append(ret['vol'])
            if 'px' in param:
                px.append(ret['px'])
      
        datadct = {'name':nameLst,'symbol':symbolLst,'day_perf':p1d,'1week_perf':p1w,'4week_perf':p4w,'12week_perf':p12w,'24week_perf':p24w}
        datacolumns=['name','symbol','day_perf','1week_perf','4week_perf','12week_perf','24week_perf']
        if 'px' in param:
            datadct['px'] = px
            datacolumns.append('px')
        if 'ma10' in param: 
            datadct['ma10'] = ma10
            datacolumns.append('ma10')
        if 'ma50' in param: 
            datadct['ma50'] = ma50
            datacolumns.append('ma50')
        if 'ma200' in param: 
            datadct['ma200'] = ma200
            datacolumns.append('ma200')
        if 'vol20' in param:
            datadct['vol20'] = vol20
            datacolumns.append('vol20')
        if 'vol' in param:
            datadct['vol'] = voltd
            datacolumns.append('vol')
                
        table = pandas.DataFrame(datadct, columns=datacolumns)
        print "\n=== sort by 24week,12week,4week,1week===========================\n"
                
        print table.sort_index(by=['24week_perf','12week_perf','4week_perf','1week_perf'],\
            ascending=[False,False,False,False])
            
        print "\n=== best in 1week,4week,12week together=========================\n"
        #meet top3-4week,top10-12week,top20-24week together
        top1w = table.sort_index(by='1week_perf',ascending=False).head(3)['symbol']
        top4w = table.sort_index(by='4week_perf',ascending=False).head(10)['symbol']
        top12w = table.sort_index(by='12week_perf',ascending=False).head(20)['symbol']
        bmz1 = table[(table['symbol'].isin(top1w)) & (table['symbol'].isin(top4w)) & (table['symbol'].isin(top12w))]
        print bmz1      
        
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