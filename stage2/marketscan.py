'''
"marketscan.py -f <portfolio_file> -g "strategy&ckd=2015-03-12" -i portfolio_id_mask(0:all) -t 'MSFT,AAPL' [-s 2010-01-01 -e 2014-12-30]"
'''
import getopt
import datetime
import sys
import os
from timeit import default_timer as timer
#sys.path.insert(0, "../strategies/")


import pandas.io.data as web
import pandas
import csv
import marketdata  #->ms_marketdata
import ms_csvchart
import ms_backtest
import pandas
#import xlsxwriter
from feed_sina import SinaMarketData
from feed_yahoo import FeederYahoo
import ms_paramparser
import ms_config
import ms_feed
from collections import OrderedDict



class MarketScan:
    class RawData:
        def __init__(self):
            print "raw data init"
            self.ohlc = {}
            self.table = {}
            self.strategy = {}
            pass
            
    def __init__(self):
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False) #expand wide dataframe
        pandas.set_option('display.max_rows', 1500)
        #pandas.set_option('display.width', 100)
        #pandas.set_option('max_colwidth', 600)
        
        #pandas.set_option('display.float_format', lambda x: '%.3f' % x)
                
        self.outputpath = "../result/"

        #self.mscfg = "./marketscan.cfg" #??
        self.mtd = marketdata.MarketData()
        self.mfeed = ms_feed.ms_feed()
        self.csvchart = ms_csvchart.ms_csvchart()
        self.params = ms_paramparser.ms_paramparser()
        self.datacfg = ms_config.MsDataCfg("")
        self.cachepath = self.datacfg.getDataConfig("folder","../cache/")  
        self.sgyInx={}
        self.rawData = {} #MarketScan.RawData()
        
        #self.sp500 = "^GSPC" #?
        #self.nmuBest = 1 #??      
          
        return

    def usage(self):
        print "marketscan.py -f <portfolio_file> -g strategy&parameter=value -i portfolio_id_mask(0:all) -t 'MSFT,AAPL' [-s 2010-01-01 -e 2014-12-30]"
        print 'run marketscan.py -g "st_perf" -i 1,2,3 --loadmd -h'
 
    def parseOption(self,args): 
        #print "parse option"        
        params = self.params
        params.parseOption(args)
        self.mfeed.initOption(params) # must change feed params
        if (params.hasBackTest):
            self.backtest = ms_backtest.ms_backtest()
            
        if not params.sgyparam:
            #params.sgyparam = self.loadCfg(self.mscfg)
            pass
        else:        
            self.loadStrategy(params.sgyparam)           
   
        
    def loadStrategy(self,sgyLst):
        #load all strategy
        #sys.path.insert(0, "../strategies/")
        self.sgyInx = {}
        for sgy in sgyLst:
            print sgy
            module_meta = __import__(sgy, globals(), locals(), [sgy])
            c = getattr(module_meta, sgy) 
            myobject = c() # construct module
            print "created strategy=",sgy
            self.sgyInx[sgy] = myobject
            if self.params.help == True:
                print sgy,myobject.usage()
                
        return 
        
   

        
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
        
        # excel
        #self.saveExcelFile(table,saveFileName)
     
    def getSaveFileName(self,addstr=""):
        saveFileName = "scan_"
        for sgyname in self.sgyInx:
            saveFileName += sgyname
            saveFileName +="_"
            
        if addstr != "":
            saveFileName = saveFileName + addstr + "_"
        return saveFileName

    def saveExcelFile(self,table,saveFileName,offset = 2):
        # save to excel
        #try:
        outputFnXls = self.outputpath + saveFileName + datetime.datetime.now().strftime("%Y-%m-%d") + '.xls'
        writer = pandas.ExcelWriter(outputFnXls, engine='xlsxwriter')            
        table.to_excel(writer, index=False, sheet_name='report')
        workbook = writer.book
        worksheet = writer.sheets['report']

        format1 = workbook.add_format({'bg_color': '#FFC7CE','font_color': '#9C0006','bold': True})
        format2 = workbook.add_format({'bg_color': '#C6EFCE','font_color': '#006100','bold': True})
        #find the two largest and smallest value
        #offset = 2 #symbol,exg            
        for col in table:
            if col=='symbol' or col=='exg':
                continue
            lvalue = table[col].max()
            svalue = table[col].min()
            lidx = table[col].idxmax()
            sidx = table[col].idxmin()
            #print lidx,lvalue,sidx,svalue
            #worksheet.write('B1', 'Cost', format1)            
            worksheet.write_string(lidx+1,offset,str(lvalue),format1)
            worksheet.write_string(sidx+1,offset,str(svalue),format2)
            offset+=1

        writer.save()
        print "Finish wrote to ",outputFnXls
        #except:
        #    print "exception when write to excel ",outputFnXls
        pass    
            
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
    '''
    def addSP500(self,df):
        df1 = df[df['symbol'].isin(['^GSPC'])]
        if df1.empty:
            print "no sp500"
            df.loc[len(df)+1,'symbol'] = self.sp500    
        else:
            print "sp500 in"

        return
    ''' 
    def loadDataTask(self,args=""):
        if (args!=""):
            #called by daemon
            self.parseOption(args.split())
        symboldf = self.params.getSymbolDf()
        self.rawData[self.params.feed] = MarketScan.RawData()
        feedData = self.rawData[self.params.feed]
        feedData.table = symboldf 
        print "Loading task, feed=",self.params.feed
        start = timer()
        for index, row in symboldf.iterrows():
            symbol = row['symbol']
            goog = row['goog']
            googexg = row['googexg']
            sina =  row['sina']
            '''
            try:
                goog = row['goog']
                googexg = row['googexg']
                sina =  row['sina']
            except:
                goog = symbol
                googexg=""
                sina=symbol
            '''
            ohlc = self.mfeed.getOhlc(symbol,sina,goog,googexg)
            if (ohlc is None):
                print symbol,"doesn't have ohlc data"
                continue
            feedData.ohlc[symbol] = ohlc

       
        end = timer()  
        print "\ttime",round(end - start,3)        
        return feedData 
    
    def getStrategyCache(self,feedData, symbol,sgyname):
        #save to stategy 
        if (sgyname not in feedData.strategy):
            feedData.strategy[sgyname] = {}
        sgycache = feedData.strategy[sgyname]
        
        if (symbol not in sgycache):                  
            sgycache[symbol] = {}
            
        sgysymbol = sgycache[symbol]
        #print sgysymbol
        return sgysymbol
    '''    
    def getStrategyCache(self,feedData, sgyname):
        #save to stategy 
        if (sgyname not in feedData.strategy):
            feedData.strategy[sgyname] = {}
        sgycache = feedData.strategy[sgyname]
        return sgycache
    ''' 
    def debug(self):
        pass
        
    #support one arg only
    def scanTask(self,args=""):
        if (args!=""): #called by daemon
            self.parseOption(args.split())  
            
        df1 = self.params.getSymbolDf()
        tickdct = {}
        for symbol in df1['symbol']:
            tickdct[symbol]=1
        
        outputCol = OrderedDict({'symbol':1,'px':1})  
        #feedData.table = df1 #deepcopy?  TODO
        #table = feedData.table
        #print type(table),id(table)
        #print type(feedData.table),id(feedData.table)
        #sys.exit()
        # load prescan module        
        noPxModule = True
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            if sgx.needPriceData()==False:
                print "total", len(df1.index),"symbols selected to be processed by",sgyname
                sgx.setupParam(self.params.sgyparam[sgyname])
                tblout,cols = sgx.process(df1)
                for key in cols:
                    outputCol[key] = 1

                #print tblout
                #merge tblout & df1
                df1 = pandas.merge(tblout,df1,how='inner')                
            else:
                noPxModule = False
        
    
        try:
            feedData = self.rawData[self.params.feed]      
        except:
            #not load yest
            #feedData = self.loadDataTask(args)
            print "you need to load data firstly. e.g.(load1d)"
            return
      
        #merge prescan df with table, possible to save to original table?(save time)
        #TODO
        if (noPxModule):
            print "No px module to run, done."
            feedData.table = pandas.merge(feedData.table,df1,how='outer')
            table = pandas.merge(feedData.table,df1,how='inner') #create new table
            print table
            #print "============================"
            #print table
            #print type(table),id(table)
            #print type(feedData.table),id(feedData.table)
            #print self.rawData[self.params.feed].table
            return table
            
        print "total", len(feedData.table.index),"symbols selected to run indicator/strategy"
        #print feedData.table
        #sys.exit()         
        # indicator 
        # loop each symbol
        for index, row in feedData.table.iterrows():
            symbol = row['symbol']
            if (symbol not in tickdct):
                print "skip",symbol
                continue
            #ohlc = self.mfeed.getOhlc(symbol)
            if (symbol not in feedData.ohlc):
                print symbol,"not in cache"
                continue
                
            ohlc = feedData.ohlc[symbol]
            
            #???
            #if (ohlc is None):
            #    continue                
            
            #modify the original table
            #print index,symbol,len(ohlc) #ohlc['Adj Close'][-1]
            #print ohlc['Adj Close'].iloc[-1]
            feedData.table.loc[index,'px'] = round(ohlc['Adj Close'].iloc[-1],2)
                        
            start = timer()
            
            #print self.sgyInx
            print "processing",symbol
            for sgyname in self.sgyInx:                    
                sgysymbol = self.getStrategyCache(feedData, symbol, sgyname)
                if not sgysymbol: 
                    sgx = self.sgyInx[sgyname]                    
                    if (sgx.needPriceData()):
                        print "\t",sgyname
                        sgx.cleanup()
                        sgx.setupParam(self.params.sgyparam[sgyname])
                        sgx.runIndicator(symbol,ohlc,self.params.sgyparam[sgyname])
                        indarr = sgx.getIndicators()
                        #read indicator
                        for cn in indarr:
                            feedData.table.loc[index,cn] = indarr[cn]
                            sgysymbol[cn] = indarr[cn]                            
                else:
                    #indarr = sgysymbol  
                    pass # do noting                      

                

                if (self.params.verbose):
                    print ohlc                   
                
                
                # if backtest...
                if (self.params.hasBackTest):
                    self.backtest.runBackTest(symbol,ohlc)
                    pass
            
            end = timer()  
            print "\ttime",round(end - start,3)     
        

        #filter work
        #table=feedData.table[(feedData.table['symbol'].isin(df1['symbol']))]
        #merge here -- because there is no only NoPriceModule.
        table = pandas.merge(feedData.table,df1,how='inner')
        #print table
        #print "================="
        #print feedData.table
        #sys.exit()
        print "=== screening ===="
        #outputCol = OrderedDict({'symbol':1,'px':1})
        #outputCol = ['symbol','px']
        
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            if sgx.needPriceData()==True: #allow ms_zack to run scan
                print "screening ",sgyname
                sgx = self.sgyInx[sgyname]
                print "screen param",self.params.sgyparam[sgyname]
                sgx.setupParam(self.params.sgyparam[sgyname])
                table,cls = sgx.runScan(table)
                
                #outputCol.append(cls)
                for key in cls:
                    outputCol[key] = 1#.append(key)#[key]=1
    

        #colLst = table.columns.values
        #print "output column list",outputCol
        table = table[outputCol.keys()]
        # daily report file
        of = self.datacfg.getDataConfig("output_report")

        with open(of, "a") as reportfile:
            print >>reportfile, "\n\n==== ",self.getSaveFileName()," =====\n"
            print >>reportfile, table.to_string(index=False)
        
        #get columne we need only!    

        print table          
        
        #save filted csv file
        self.saveTableFile(table)
        # trigger csv chart
        if self.params.haschart:
            print "=== csv chart ==="
            self.csvchart.drawChart(table,self.chartparam)
        
        ''' 
        print "===============original table ============="   
        print feedData.table
        '''
        return table
        #print self.rawData
        pass
          
    def standalone(self):
        self.parseOption(sys.argv[1:])
        self.loadDataTask()
        self.scanTask()
        pass
  
    def printOhlcTask(self,arg):
        #feed=""
        #symbol = arg.upper()
        print arg
        print "======================"
        self.parseOption(arg.split())
        feed = self.params.feed
        
        #print feed
        #print self.params.tickdf
        
        if (feed not in self.rawData):
            print "Not loaded data yet"            
            return
        feedData = self.rawData[feed]
        
        for index, row in self.params.tickdf.iterrows():
            symbol = row['symbol']
            if (symbol in feedData.ohlc):
                print feedData.ohlc[symbol]                
            else:
                print "Not found"        
        pass
          
    def procMarketData(self):
        if self.params.tickdf.empty:
            print "loading from symbolfile..."
            #df = self.loadSymbolLstFile(self.params.symbolLstFile) move to mtd
            df = self.mtd.loadSymbolLstFile(self.params.symbolLstFile)
            df1 = self.mtd.getSymbolByPid(df,self.params.pid)[['symbol']]
            ticklist = df1['symbol']
        else:
            print "using ticklist from command line..."            
            df1 = self.params.tickdf            
            #ticklist = self.ticklist     
        
        #load prescan module
        noPxModule = True
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            if sgx.needPriceData()==False:
                print "total", len(df1.index),"symbols selected to be processed by",sgyname
                tblout = sgx.process(df1,self.params.sgyparam[sgyname])
                #merge tblout & df1
                df1 = pandas.merge(tblout,df1,how='inner')
            else:
                noPxModule = False
                        
        #TODO not add index
        #self.addSP500(df1)
                    
        print "==================================================="
        if (noPxModule):
            #save raw csv file        
            self.saveTableFile(df1,"raw")
            print df1
            return df1

        print "total", len(df1.index),"symbols selected to run indicator/strategy"
        '''
        allow to download data even that no price module
        if self.hasPriceDataModule()==False and self.params.haschart==False:
            self.saveTableFile(df1,"raw")
            print df1
            print "No more pricedata module to be processed, exit..."
            return
        '''
        
        # process pricedata module 
        table = self.runIndicator(df1)

        #save raw csv file        
        self.saveTableFile(table,"raw")
        print table
        
        #filter work
        print "=== screening ===="
        outputCol = OrderedDict({'symbol':1,'px':1})
        #outputCol = ['symbol','px']
        for sgyname in self.sgyInx:
            sgx = self.sgyInx[sgyname]
            #if sgx.needPriceData()==True: allow ms_zack to run scan
            print "screening ",sgyname
            sgx = self.sgyInx[sgyname]
            table,cls = sgx.runScan(table)
            #outputCol.append(cls)
            for key in cls:
                outputCol[key] = 1#.append(key)#[key]=1
    
        #colLst = table.columns.values
        #print "output column list",outputCol
        table = table[outputCol.keys()]
        # daily report file
        of = self.datacfg.getDataConfig("output_report")

        with open(of, "a") as reportfile:
            print >>reportfile, "\n\n==== ",self.getSaveFileName()," =====\n"
            print >>reportfile, table.to_string(index=False)
        
        #get columne we need only!    

        print table          
        
        #save filted csv file
        self.saveTableFile(table)
        # trigger csv chart
        if self.params.haschart:
            print "=== csv chart ==="
            self.csvchart.drawChart(table,self.chartparam)
        return table     
       
    def runIndicator(self, table):
        #TODO if no post-module, should return immediately
        numError = 0
        id = 0
        self.mfeed.initOption(self.params)
        
        for index, row in table.iterrows():
            symbol = row['symbol']
            #print "downloading ",id, symbol
            id+=1            
            ohlc = self.mfeed.getOhlc(symbol)
            if (ohlc is None):
                continue
            #add 'px' column
            #print "intc",ohlc['Adj Close']
            table.loc[index,'px'] = round(ohlc['Adj Close'][-1],2)
            start = timer()
            print "processing",symbol
            #print self.sgyInx
            for sgyname in self.sgyInx:
                #if not sgyname in self.sgyInfo:
                sgx = self.sgyInx[sgyname]
                #if sgx.needPriceData()==True:
                sgx.cleanup()
                sgx.setupParam(self.params.sgyparam[sgyname])
                sgx.runIndicator(symbol,ohlc,self.params.sgyparam[sgyname])
                if (self.params.verbose):
                    print ohlc
                #TODO if backtest skip this?
                #strategy should only return 1 buy signal column
                indarr = sgx.getIndicators()
                for cn in indarr:
                    table.loc[index,cn] = indarr[cn]
                
                # if backtest...
                if (self.params.hasBackTest):
                    self.backtest.runBackTest(symbol,ohlc)
                    pass
            end = timer()  
            print "\ttime",round(end - start,3)
        if (self.params.hasBackTest):
            backtestDf = self.backtest.getBackTestResult()
            print "========================="
            print backtestDf
            print "========================="
            self.saveExcelFile(backtestDf,self.getSaveFileName(),1) #offset=1
        return table
   

    def process(self, args=""):
        if (args==""):
            self.parseOption(sys.argv[1:])
        else:
            self.parseOption(args.split())
        return obj.run()   
        #return self.procMarketData()
        
if __name__ == "__main__":
    obj = MarketScan()
    obj.standalone()
    
 
 
 