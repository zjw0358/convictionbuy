import getopt
import datetime
import sys
import pandas.io.data as web
import pandas

class PerfScreen:
    def __init__(self):
        self.columns = ['symbol','5d','10d','20d', '50d', '100d','200d','max','px', \
                        'sma10','sma50','sma200','sma10%','sma50%','sma200%']
        self.perftable = pandas.DataFrame(columns=self.columns) 
        self.outputpath = "../result/"
        #pandas.options.display.float_format = '{:,.2f}%'.format
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
        print "parse option"
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
            self.usage()
            sys.exit()

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
  
    def process(self):
        self.parseOption()
        self.runPerfCompare()
        self.makeReport()
        
if __name__ == "__main__":
    obj = PerfScreen()
    obj.process()
    #process(sys.argv[1:],None)