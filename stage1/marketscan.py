
import getopt
import datetime
import sys
#sys.path.insert(0, "../strategy/")
#sys.path.insert(0, "../screen/")

import pandas.io.data as web
import pandas
#import fundata
import csv

#sys.path.insert(0, "../src/")
#import simutable
#import tradesupport
'''
historical price
http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv

'''
class MarketScan:
    def __init__(self):
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        #pandas.options.display.float_format = '{:,.2f}%'.format
        pandas.set_option('display.float_format', lambda x: '%.3f' % x)
                
        self.outputpath = "../result/"        
        self.enddate = ""
        self.startdate = ""
        self.symbolLstFileCol = ['symbol','rank','name','sector','industry','pid','exg'] 
        self.symbolLstFile = "./marketdata.csv"  #default marketdata file
        self.pid = 1 #0-dow30,1-zr focus list,2-jpm/zack list
        self.mscfg = "./marketscan.cfg"
        self.sp500 = "^GSPC"
        self.nmuBest = 1 #??
        #self.tradesup = tradesupport.Trade(self)
        #self.simutable = simutable.SimuTable(self)
        #self.tradesup.setMode(2) #no trade log
        #self.simutable.setMode(2) #no trade log
        self.sgyparam = {}
        self.ticklist = []
        
        # strategy info, 0 - run before download price;        
        # module run before scan aka FA module
        # TODO put this info in config file later
        #self.sgyInfo = {'ms_pvm':0,"ms_reuter":0,"zack_data":0}
        
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
        print "program -f <portfolio_file> -g strategy&ckd=2015-03-12 -i portfolio_id_mask -t 'MSFT,AAPL' [-s 2010-01-01 -e 2014-12-30]"
 
    def parseOption(self):
        print "=========================="
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:s:e:i:g:", \
                ["filename", "ticklist", "startdate","enddate","pid","strategy"])
        except getopt.GetoptError:
            print "parse option error"
            return False

        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.symbolLstFile = arg
                #self.option = 1
            elif opt in ("-t", "--ticklist"):
                newstr = arg #.replace("", "")                
                self.ticklist = newstr.split(",")
            elif opt in ("-s", "--startdate"):
                self.startdate = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
            elif opt in ("-i", "--pid"):
                self.pid = int(arg)
            elif opt in ("-g", "--strategy"):
                self.sgyparam = self.parseStrategy(arg)
                                   
        if self.enddate == "":
            self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
            if not self.startdate:
                startday = datetime.date.today() - datetime.timedelta(days=365)
                self.startdate = startday.strftime("%Y-%m-%d")

        if not self.sgyparam:
            self.sgyparam = self.loadCfg(self.mscfg)
        #load strategy
        self.loadStrategy(self.sgyparam)           
        #self.funda = fundata.FundaData()

        print "use ", self.symbolLstFile
        print "start date", self.startdate
        print "end date", self.enddate
        print "portfolio id mask ",self.pid
        print "=========================="
    '''
    st_rsi&cl=14,st_macd&f=10&s=5
    ms_pvm&download&pe<20&mc>1000
    '''    
    def parseStrategy(self,arg):
        l_sgy = {}
        for item in arg.split(","):
            idx = 0
            param = {}
            for token in item.split("&"):
                if idx == 0:                    
                    l_sgy[token] = param
                else:
                    k= token.split('=')
                    if (len(k)>1):
                        param[k[0]] = k[1]
                    else:
                        param[k[0]] = ""
                idx += 1
        print l_sgy
        return l_sgy
        

    '''
    the 'marketscan.cfg' would be 
    st_rsi,xxx=1&yyy=1
    st_macd,...
    ...
    create strategy
    '''  
    def loadCfg(self,fileName): #TODO
        #strategy_name,parameter
        fp = open(fileName,'r',-1)
        sgyLst = {}
        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        try:
            for row in reader:
                sgyLst[row[0]] = row[1]
                idx += 1
        except:
            print "error when reading marketscan cfg file, exit..."
            sys.exit()
        fp.close()      # closing
        return sgyLst        
        
    def loadStrategy(self,sgyLst):
        #load all strategy
        self.sgyInx = {}
        for sgy in sgyLst:
            module_meta = __import__(sgy, globals(), locals(), [sgy])
            c = getattr(module_meta, sgy) 
            myobject = c() # construct module
            print "created strategy=",sgy
            self.sgyInx[sgy] = myobject
            #add strategy to trade order decision matrix
            #self.tradesup.addStrategy(myobject.getStrategyName())

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

         
    #def getSymbolLstCol(self):
    #    return self.symbolLstFileCol
        
    def saveTableFile(self,table,addstr=""):
        saveFileName = "scan_"
        for sgyname in self.sgyInx:
            saveFileName += sgyname
            saveFileName +="_"
            
        if addstr != "":
            saveFileName = saveFileName + addstr + "_"
            

        outputFn = self.outputpath + saveFileName + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        try:
            table.to_csv(outputFn,sep=',',index=False)
            print "Finish wrote to ",outputFn
        except:
            print "exception when write to csv ",outputFn
            
    # get symbol by pid
    def getSymbolByPid(self):
        # load symbol list file
        df = self.loadSymbolLstFile(self.symbolLstFile)
        
        #filter via pid mask
        if self.pid>0:
            criterion = df['pid'].map(lambda x: (int(x)&self.pid>0))
            df1 = df[criterion] 
        else: #all 
            df1 = df
        return df1
        
    def getSymbolByRank(self,table,rmin,rmax):
        df = table[(table['rank']<=rmax) & (table['rank']>=rmin)]
        return df
        
    # iterate all modules to see if there is price data module
    # return True - pricedata module
    # return False - no pricedata module
    def hasPriceDataModule(self):
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            if sgx.needPriceData()==True:
                return True
        return False
        
    def procMarketData(self):
        if not self.ticklist:
            df1 = self.getSymbolByPid()[['symbol']]
            ticklist = df1['symbol']
        else:
            df1 = pandas.DataFrame(self.ticklist,columns=['symbol'])
            ticklist = self.ticklist     
        
        #load prescan module
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            if sgx.needPriceData()==False:
                print "total", len(df1.index),"symbols selected to be processed by",sgyname
                tblout = sgx.process(df1,self.sgyparam[sgyname])
                #merge tblout & df1
                df1 = pandas.merge(tblout,df1,how='inner')
                    
        #df = df1[(df1['symbol'].isin(ticklist)) | (df1['symbol']==self.sp500)]
        # add S&P500 as benchmark
        df1.loc[len(df1)+1,'symbol'] = self.sp500    
                
        print "==================================================="
        print "total", len(df1.index),"symbols selected"
        if self.hasPriceDataModule()==False:
            self.saveTableFile(df1,"raw")
            print df1
            print "No more pricedata module to be processed, exit..."
            return

        # process pricedata module 
        table = self.runIndicator(df1)

        #save raw csv file        
        self.saveTableFile(table,"raw")
        print table
        #filter work
        print "=== screening ===="
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            if sgx.needPriceData()==True:
                print "screening ",sgyname
                sgx = self.sgyInx[sgyname]
                table = sgx.runScan(table)
        print table
        #save filted csv file
        self.saveTableFile(table)
        
        return       
         
    
    def runIndicator(self, table):
        #TODO if no post-module, should return immediately
        numError = 0            
        for index, row in table.iterrows():
            symbol = row['symbol']
            print "processing ",index, symbol
            try:
                ohlc = web.get_data_yahoo(symbol, self.startdate, self.enddate)
                '''
                dateidx = ohlc.index
                print ohlc.loc['2014-04-01']
                print ohlc.index.get_loc('2014-04-01')
                print type(ohlc.index)
                print ohlc.loc['2014-04-01']['Open']
                '''
                #print ohlc
            except:
                numError += 1
                print "System/Network Error when retrieving ",symbol," skip it"
                if numError>3:
                    print "too many errors when downloading symbol data, exit now"
                    sys.exit()
            
            for sgyname in self.sgyInx:
                #if not sgyname in self.sgyInfo:
                sgx = self.sgyInx[sgyname]
                if sgx.needPriceData()==True:
                    sgx.runIndicator(symbol,ohlc,self.sgyparam[sgyname]) #parameter
                    indarr = sgx.getIndicators()
                    for cn in indarr:
                        table.loc[index,cn] = indarr[cn]
               

            
            #break
        #print table
        return table
        
    def process(self):
        self.parseOption()
        self.procMarketData()
        
if __name__ == "__main__":
    obj = MarketScan()
    obj.process()
 