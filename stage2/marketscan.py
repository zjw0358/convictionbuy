'''
"marketscan.py -f <portfolio_file> -g "strategy&ckd=2015-03-12" -i portfolio_id_mask(0:all) -t 'MSFT,AAPL' [-s 2010-01-01 -e 2014-12-30]"
'''
import getopt
import datetime
import sys
import os
from timeit import default_timer as timer


import pandas.io.data as web
import pandas
import csv
import marketdata  #->ms_marketdata
import ms_csvchart
import ms_backtest
import pandas
import ms_paramparser
import ms_config
import ms_feed
from collections import OrderedDict

# global func ---------------------------------
g_marketscan = None
def importStrategy(sgyname, symbol, ohlc):
    return g_marketscan.importStrategy(sgyname, symbol, ohlc)
    pass


class marketscan:
    class RawData:
        def __init__(self):
            #print "raw data init"
            self.ohlc = {}
            self.table = {}
            self.strategy = {}
            self.dirty = True

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
        self.backtest = ms_backtest.ms_backtest()
        self.csvchart = ms_csvchart.ms_csvchart()
        self.params = ms_paramparser.ms_paramparser()
        self.datacfg = ms_config.MsDataCfg("")
        self.cachepath = self.datacfg.getDataConfig("folder","../cache/")           
        self.sgyInxDct={}
        self.rawData = {} #MarketScan.RawData()
        global g_marketscan
        g_marketscan = self
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
        #if (params.hasBackTest):
        #    self.backtest = ms_backtest.ms_backtest()
            
        if not params.sgyparam:
            #params.sgyparam = self.loadCfg(self.mscfg)
            pass
        else:        
            self.loadStrategy(params.sgyparam)           
   
        
    def loadStrategy(self, sgyParamDct):
        #load all strategy
        #sys.path.insert(0, "../strategies/")
        self.sgyInxDct = {}
        self.sgyInxAllDct = {}
        for sgy in sgyParamDct:
            module_meta = __import__(sgy, globals(), locals(), [sgy])
            c = getattr(module_meta, sgy) 
            myobject = c() # construct module
            sgyParamDct[sgy]['verbose'] = self.params.verbose
            print "created strategy", sgy, sgyParamDct[sgy]
            self.sgyInxDct[sgy] = myobject
            self.sgyInxAllDct[sgy] = myobject
            if self.params.help == True:
                print sgy,myobject.usage()
                
        return

    # import indicator
    def importStrategy(self, sgyname, symbol, ohlc):
        sgx = self._getStrategyInx(sgyname)
        self._runStrategy(symbol, ohlc, sgyname)
        return sgx

    # TODO update sgyInxDct
    def _getStrategyInx(self, sgy):
        if sgy not in self.sgyInxAllDct:
            module_meta = __import__(sgy, globals(), locals(), [sgy])
            c = getattr(module_meta, sgy)
            myobject = c() # construct module
            if sgy not in self.params.sgyparam:
                self.params.sgyparam[sgy] = {}
            self.params.sgyparam[sgy]['verbose'] = self.params.verbose
            print "created strategy", sgy, self.params.sgyparam[sgy]
            self.sgyInxAllDct[sgy] = myobject
        return self.sgyInxAllDct[sgy]
   
    def _runStrategy(self, symbol, ohlc, sgyname):
        cacheflag = self._hasStrategyCache(self.feedData, symbol, sgyname, self.params.sgyparam[sgyname])
        if not cacheflag:
            sgx = self.sgyInxAllDct[sgyname]
            if sgx.needPriceData():
                if self.params.verbose > 1:
                    print "\t", sgyname
                sgx.cleanup()
                sgx.setupParam(self.params.sgyparam[sgyname])
                # ohlc = self.feedData.ohlc[symbol]
                sgx.runIndicator(symbol, ohlc, self.params.sgyparam[sgyname])
                #indarr = sgx.getIndicators()
                #for cn in indarr:
                #    self.feedData.table.loc[index,cn] = indarr[cn]
        #return  self.sgyInxAllDct[sgyname]


        
    def saveTableFile(self,table,addstr=""):
        saveFileName = "scan_"
        for sgyname in self.sgyInxDct:
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
        for sgyname in self.sgyInxDct:
            saveFileName += sgyname
            saveFileName +="_"
            
        if addstr != "":
            saveFileName = saveFileName + addstr + "_"
        return saveFileName


   
    # iterate all modules to see if there is price data module
    # return True - pricedata module
    # return False - no pricedata module
    def hasPriceDataModule(self):
        for sgyname in self.sgyInxDct:
            sgx = self.sgyInxDct[sgyname]
            if sgx.needPriceData()==True:
                return True
        return False
   
    # load data into cache from file
    def loadDataTask(self,args=""):
        if (args!=""):
            #called by daemon
            self.parseOption(args.split())
        symboldf = self.params.getSymbolDf()
        self.rawData[self.params.feed] = marketscan.RawData()
        feedData = self.rawData[self.params.feed]
        feedData.table = symboldf 
        print "loadDataTask..."
        start = timer()
        for index, row in symboldf.iterrows():
            symbol = row['symbol']
            goog = row['goog']
            googexg = row['googexg']
            sina =  row['sina']
            
            ohlc = self.mfeed.getOhlc(symbol,sina,goog,googexg)
            
            if (ohlc is None):
                print symbol,"doesn't have ohlc data"
                continue
            feedData.ohlc[symbol] = ohlc
        end = timer()  
        feedData.dirty = True
        print "\tfinished with time",round(end - start,3)        
        return feedData 
    
   
    def _hasStrategyCache(self, feedData, symbol, sgyname, sgyparam):
        cacheflag = True
        if ((sgyname,symbol) in feedData.strategy):
            sgycache = feedData.strategy[(sgyname,symbol)]
            #compare param
            for key in sgyparam:
                if (key!="verbose") and (sgyparam[key]!='') and (sgycache[key]!=sgyparam[key]) :
                    cacheflag = False
                    break
            if (cacheflag):
                #print symbol,sgyname,"has cache",sgycache
                return True #has cache
            
        #else create new strategy record
        feedData.strategy[(sgyname,symbol)] = {}
        cache = feedData.strategy[(sgyname,symbol)]
        cache.update(sgyparam)
        return False
    

    #support one arg only
    def scanTask(self,args=""):
        if (args!=""): #called by daemon
            self.parseOption(args.split())  
            
        df1 = self.params.getSymbolDf()
        tickdct = {}
        for symbol in df1['symbol']:
            tickdct[symbol]=1
        
        # output column
        outputCol = OrderedDict({'symbol':1,'px':1}) 
        # load prescan module        
        noPxModule = True
        for sgyname in self.sgyInxDct:
            sgx = self.sgyInxDct[sgyname]
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
            self.feedData = self.rawData[self.params.feed]
            if (self.feedData.dirty):
                print "clear current [",self.params.feed,"] strategy cache"
                self.feedData.strategy.clear()
            self.feedData.dirty = False
        except:
            #not load yest
            #self.feedData = self.loadDataTask(args)
            print "you need to load data firstly. e.g.(load1d)"
            return
      
        #merge prescan df with table, possible to save to original table?(save time)
        #TODO
        if (noPxModule):
            print "No px module to run, done."
            self.feedData.table = pandas.merge(self.feedData.table,df1,how='outer')
            table = pandas.merge(self.feedData.table,df1,how='inner') #create new table
            print table
            return table
            
        print "total", len(self.feedData.table.index),"symbols selected to run indicator/strategy"
        
        
        # loop each symbol
        for index, row in self.feedData.table.iterrows():
            symbol = row['symbol']
            if (symbol not in tickdct):
                #print "skip",symbol
                continue
            #ohlc = self.mfeed.getOhlc(symbol)
            if (symbol not in self.feedData.ohlc):
                print symbol, "not in cache"
                continue
                
            ohlc = self.feedData.ohlc[symbol]
            self.feedData.table.loc[index, 'px'] = round(ohlc['Adj Close'].iloc[-1],2)
            
            if (self.params.verbose > 1): 
                start = timer()
                print "processing", symbol
                
            for sgyname in self.sgyInxDct:
                cacheflag = self._hasStrategyCache(self.feedData, symbol, sgyname, self.params.sgyparam[sgyname])
                if not cacheflag: 
                    sgx = self.sgyInxDct[sgyname]
                    if (sgx.needPriceData()):
                        if (self.params.verbose > 1): 
                            print "\t", sgyname
                        sgx.cleanup()
                        sgx.setupParam(self.params.sgyparam[sgyname])
                        sgx.runIndicator(symbol, ohlc, self.params.sgyparam[sgyname])
                        indarr = sgx.getIndicators()
                        #read indicator
                        for cn in indarr:
                            self.feedData.table.loc[index,cn] = indarr[cn]
                            #sgysymbol[cn] = indarr[cn]                            
                            
                else:
                    #indarr = sgysymbol  
                    pass # do noting                      

                # if backtest...
                if (self.params.hasBackTest):
                    self.backtest.runBackTest(symbol, ohlc)
                    pass
            
            if (self.params.verbose > 1): 
                end = timer()  
                print "\ttime",round(end - start,3)     
        

        #filter work
        #table=self.feedData.table[(self.feedData.table['symbol'].isin(df1['symbol']))]
        #merge here -- because there is no only NoPriceModule.
        table = pandas.merge(self.feedData.table,df1,how='inner')
        print "=== screening ===="
        #print self.params.sgyparam
        #outputCol = OrderedDict({'symbol':1,'px':1})
        #outputCol = ['symbol','px']
        
        for sgyname in self.sgyInxDct:
        #for sgyname in self.params.sgyparam:
            sgx = self.sgyInxDct[sgyname]
            if sgx.needPriceData()==True: #allow ms_zack to run scan
                #print "screening ",sgyname
                sgx = self.sgyInxDct[sgyname]
                print "screening",sgyname,self.params.sgyparam[sgyname]
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
        print "...................."
        headers = 'index\t' + '\t'.join(table.dtypes.index)
        print headers #print column again
                        
        print "...................."
        print len(table),"/",len(self.feedData.table.index),"=",round(len(table)*100.0/len(self.feedData.table.index),2),"%"
        
        #save filted csv file
        self.saveTableFile(table)
        # trigger csv chart
        if self.params.haschart:
            print "=== csv chart ==="
            self.csvchart.drawChart(table,self.chartparam)

        return table
        #print self.rawData
        pass
          
    def standalone(self):
        self.parseOption(sys.argv[1:])
        self.loadDataTask()
        self.scanTask()
        pass

    # move to module
    def back_test(self, arg):
        self.parseOption(arg.split())
        feed = self.params.feed

        if (feed not in self.rawData):
            print "Not loaded data yet"
            return

        feed_data = self.rawData[feed]
        self.backtest.beginBackTest()
        tickdf = self.params.getSymbolDf()
        for index, row in tickdf.iterrows():
            symbol = row['symbol']
            if symbol in feed_data.ohlc:
                ohlc = feed_data.ohlc[symbol]
                self.backtest.combineSignal(ohlc, self.params.buydict, self.params.selldict)
                self.backtest.runBackTest(symbol, ohlc, self.params.verbose)
                #print feed_data.ohlc[symbol]
                #headers = 'index\t' + '\t'.join(feed_data.ohlc[symbol].dtypes.index)
               # print headers
            else:
                print "Not found"

        backtestDf = self.backtest.printBackTestResult()
        #print "==============================="
        #print backtestDf

        #print "========================="
        pass

    def printTableTask(self, arg):
        print "======================"
        self.parseOption(arg.split())
        feed = self.params.feed

        if (feed not in self.rawData):
            print "Not loaded data yet"
            return

        feed_data = self.rawData[feed]
        print feed_data.table

    def printOhlcTask(self, arg):
        print "======================"
        self.parseOption(arg.split())
        feed = self.params.feed        
        
        if (feed not in self.rawData):
            print "Not loaded data yet"            
            return

        feed_data = self.rawData[feed]
        for index, row in self.params.tickdf.iterrows():
            symbol = row['symbol']
            if symbol in feed_data.ohlc:
                print feed_data.ohlc[symbol]
                headers = 'index\t' + '\t'.join(feed_data.ohlc[symbol].dtypes.index)
                print headers
            else:
                print "Not found"  
              
        pass
          
   
   

    def process(self, args=""):
        if (args==""):
            self.parseOption(sys.argv[1:])
        else:
            self.parseOption(args.split())
        return obj.run()   
        #return self.procMarketData()
        
if __name__ == "__main__":
    obj = marketscan()
    obj.standalone()
    
 
 
 