import getopt
import datetime
import sys
import pandas.io.data as web
import pandas
import fundata
import csv
sys.path.insert(0, "../strategy/")
sys.path.insert(0, "../screen/")
sys.path.insert(0, "../src/")
import simutable
import tradesupport
'''
historical price
http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv

'''
class MarketScan:
    def __init__(self):
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        
        self.outputpath = "../result/"        
        self.enddate = ""
        self.symbolLstFileCol = ['symbol','rank','name','sector','industry','pid','exg'] 
        self.symbolLstFile = "./marketdata.csv"  #default marketdata file
        self.pid = 0 #0-dow30,1-focus list
        self.mscfg = "./marketscan.cfg"
        self.nmuBest = 1
        self.tradesup = tradesupport.Trade(self)
        self.simutable = simutable.SimuTable(self)
        self.tradesup.setMode(2) #no trade log
        self.simutable.setMode(2) #no trade log
        return
        
    def getTradeSupport(self):
        return self.tradesup

    def getSimuTable(self):
        return self.simutable

    def getResultPath(self):
        return self.outputpath
        
    def getNumBest(self):
        return self.nmuBest        

                  
    def usage(self):
        print "program -f <portfolio_file> -t aapl,msft -i portfolioid [-s 2010-01-01 -e 2014-12-30]"
        print "=== show portfolio performance ================================="
        print "program -f <portfolio_file> "
 
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:s:e:i:", \
                ["filename", "ticklist", "startdate","enddate","pid"])
        except getopt.GetoptError:
            print "parse option error"
            return False

        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.symbolLstFile = arg
                #self.option = 1
            elif opt in ("-t", "--ticklist"):
                newstr = arg #.replace("", "")                
                self.ticklist = newstr.split()
            elif opt in ("-s", "--startdate"):
                self.startdate = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
            elif opt in ("-i", "--pid"):
                self.pid = int(arg)
                   
        if self.enddate == "":
            self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
            startday = datetime.date.today() - datetime.timedelta(days=365)
            self.startdate = startday.strftime("%Y-%m-%d")

        self.loadCfg(self.mscfg)
        self.funda = fundata.FundaData()

    '''
    the 'marketscan.cfg' would be 
    st_rsi,st_macd...
    create strategy
    '''  
    def loadCfg(self,fileName):
        sgyLst = []
        try:
            fp = open(fileName,'r',-1)
            sgyLst = fp.readline().split(',')
            fp.close()
        except:
            print "Error when reading marketscan cfg file:",fileName
            sys.exit()
            
        #load all strategy
        self.sgyInx = {}
        for sgy in sgyLst:
            module_meta = __import__(sgy, globals(), locals(), [sgy])
            c = getattr(module_meta, sgy) 
            myobject = c(self)
            print "created strategy=",sgy
            self.sgyInx[sgy] = myobject
            #add strategy to trade order decision matrix
            self.tradesup.addStrategy(myobject.getStrategyName())
        return
        
    def loadSymbolLstFile(self,fileName):
        #symbol,rank,name,sector,industry,pid,exg
        fp = open(fileName,'r',-1)
        symbolLst = []
        rankLst = []
        nameLst = []
        sectorLst = []
        industryLst = []
        pidLst = []
        exgLst = []
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        try:
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
        except:
            print "error when reading symbol list file, exit..."
            sys.exit()
        fp.close()      # closing
        table = pandas.DataFrame({'symbol':symbolLst,'rank':rankLst,'name':nameLst,\
            'sector':sectorLst,'industry':industryLst,'pid':pidLst,'exg':exgLst},\
            columns=['symbol','rank','name','sector','industry','pid','exg'])
        return table

    def loadSymbolLstFilePid(self,fileName,pid):
        table=self.loadSymbolLstFile(fileName)
        bitid = 1<<pid
        #print bitid
        criterion = table['pid'].map(lambda x: (int(x)&bitid==1))
        df = table[criterion]['symbol']
        return df
        
    def getSymbolLstCol(self):
        return self.symbolLstFileCol
        
    def saveTableFile(self,table,fileName):        
        outputFn = self.outputpath + fileName + "_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        try:
            table.to_csv(outputFn,sep=',',index=False)
        except:
            print "exception when write to csv ",outputFn
            
        print "Finish wrote to ",outputFn
        
    def procMarketData(self):
        df = self.loadSymbolLstFile(self.symbolLstFile)
        bitid = 1<<self.pid
        #criteria setting
        criterion = df['pid'].map(lambda x: (int(x)&bitid==1))
        df1 = df[criterion] 

        table = self.runScan(df1)
        #self.saveTableFile(table,self.symbolLstFile+"_perf")
        
        return
        
         
    
    def runScan(self, table):  
        numError = 0            
        for index, row in table.iterrows():
            symbol = row['symbol']
            print "processing ",symbol
            try:
                ohlc = web.get_data_yahoo(symbol, self.startdate, self.enddate)
            except:
                numError += 1
                print "System/Network Error when retrieving ",symbol," skip it"
                if numError>3:
                    print "too many errors when downloading symbol data, exit now"
                    sys.exit()

            for sgy in self.sgyInx:
                sgx = self.sgyInx[sgy]
                self.tradesup.beginTrade(symbol, ohlc) 
                sgx.runStrategy(symbol,ohlc)
                self.tradesup.endTrade(sgx.getSetupInfoStr())
                key1 = "%s_1" % sgy
                key2 = "%s_2" % sgy                
                table.loc[index,key1] = sgx.getIndicatorVal()
                table.loc[index,key2] = self.tradesup.getLastTrade() #getLastSignal()                
            #break
        print table
    def process(self):
        self.parseOption()
        self.procMarketData()
        
if __name__ == "__main__":
    obj = MarketScan()
    obj.process()
 