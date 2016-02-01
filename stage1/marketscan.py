'''
"marketscan.py -f <portfolio_file> -g "strategy&ckd=2015-03-12" -i portfolio_id_mask(0:all) -t 'MSFT,AAPL' [-s 2010-01-01 -e 2014-12-30]"
'''
import getopt
import datetime
import sys
import os
from timeit import default_timer as timer
sys.path.insert(0, "../strategies/")


import pandas.io.data as web
import pandas
import csv
import marketdata
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



'''
historical price
http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv

call strategy module
'''
class MarketScan:
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
        self.sp500 = "^GSPC" #?
        self.nmuBest = 1 #??      
          
        return

    def usage(self):
        print "marketscan.py -f <portfolio_file> -g strategy&parameter=value -i portfolio_id_mask(0:all) -t 'MSFT,AAPL' [-s 2010-01-01 -e 2014-12-30]"
        print 'run marketscan.py -g "st_perf" -i 1,2,3 --loadmd -h'
 
    def parseOption(self,args):         
        params = self.params
        params.parseOption(args)
        if ("sina" in params.feed):
            self.sinaapi = SinaMarketData()
        if ("yahoo" in params.feed):
            self.yahoofeed = FeederYahoo()
            
        if (params.hasBackTest):
            self.backtest = ms_backtest.ms_backtest()
            
        if not params.sgyparam:
            #params.sgyparam = self.loadCfg(self.mscfg)
            pass
        else:        
            self.loadStrategy(params.sgyparam)           
   
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
        
    #TODO move to marketdata module?  
    '''
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
    '''
         
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

    def addSP500(self,df):
        df1 = df[df['symbol'].isin(['^GSPC'])]
        if df1.empty:
            print "no sp500"
            df.loc[len(df)+1,'symbol'] = self.sp500    
        else:
            print "sp500 in"

        return
        
    '''
    main entry
    '''        
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
    '''   
    #save ohlc to csv file
    def saveOhlc(self, symbol, ohlc):
        #delete file firstly
        filename = self.cachepath + symbol + "_ohlc_" + self.params.feed + ".csv"
        try:
            os.remove(filename)
        except:
            print "unable to delete file",filename
            pass
        ohlc.to_csv(filename,sep=',')
        pass
      
    def loadOhlc(self,symbol):
        filename = self.cachepath + symbol + "_ohlc_" + self.params.feed + ".csv"
        print "loading",filename
        try:
            ohlc = pandas.read_csv(filename,index_col=['Date'])
        except:
            ohlc = pandas.DataFrame()
            return ohlc
        
        ohlc.index = pandas.to_datetime(ohlc.index)  
        date1 = datetime.datetime.strptime(self.params.startdate,'%Y-%m-%d')
        date2 = datetime.datetime.strptime(self.params.enddate,'%Y-%m-%d')
        #print date1,date2
        #unable to get next business day
        start = -1
        end = -1
        for idx,item in enumerate(ohlc.index):
            #print item,type(item)
            #print idx,item
            if (start==-1 and item >= date1):
                start = idx
                #print "start",item                
            if item >= date2:
                end = idx
                print "end",item
                break

        if (end==-1):
            end=len(ohlc.index)
        #print start,end
        ohlc = ohlc.iloc[start:end]
        return ohlc
    '''      
    def runIndicator(self, table):
        #TODO if no post-module, should return immediately
        numError = 0
        id = 0
        self.mfeed.initOption(self.params)
        
        for index, row in table.iterrows():
            symbol = row['symbol']
            #print "downloading ",id, symbol
            id+=1
            '''
            start = timer()
            
            if (self.params.loadmd):
                ohlc = self.loadOhlc(symbol)
                if ohlc.empty:
                    print symbol," marketdata is not in cache, skip it"
                    continue             
            else:
                try:
                    if ("sina" in self.params.feed):
                        ohlc = self.sinaapi.reqHisData(symbol)
                    elif ("yahoo" in self.params.feed):
                        ohlc = self.yahoofeed.reqHisData(symbol,self.params.feed,self.params.startdate, self.params.enddate)
                    else:
                        ohlc = web.get_data_yahoo(symbol, self.params.startdate, self.params.enddate)
                        
                    if (self.params.savemd):
                        self.saveOhlc(symbol,ohlc)
                except:
                    numError += 1
                    print "System/Network Error when retrieving ",symbol," skip it"                    
                    continue
            # adjust adj close price.
            ohlc = self.mtd.adjClosePrice(ohlc)       
            end = timer()  
            print "\ttime",round(end - start,3)
            '''
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
            
        return self.procMarketData()
        
if __name__ == "__main__":
    obj = MarketScan()
    obj.process()
 
 
 