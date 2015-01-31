

import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

import sys
import getopt

#from datetime import datetime
import simutable
import tradesupport
sys.path.insert(0, "../strategy/")
sys.path.insert(0, "../screen/")
import marketdata

import testreport
import matplotlib.pyplot as plt
import pandas.io.data as web
import pandas
import datetime
import glob #list files
import re   # replace char 

   
# sharpe
'''def getSharpe(dayvalue):
     daily_rets = dayvalue.pct_change()
     daily_sr = lambda x:x.mean()/x.std()
     compound = lambda x:(1+x).prod()-1
     #print "daily return"
     #for index in range(0, len(daily_rets)):
     #   print index,sdatelabel[index],daily_rets.iloc[index],dayvalue.iloc[index]
     #returns = daily_rets.resample('1B',how=compound)
     return daily_sr(daily_rets)*np.sqrt(252)'''

class BackTest:
    def __init__(self):       
        self.parameter = {}
        self.stgyBatchCfg = []
        #default log to file, unless specified in parameter
        #sys.stdout = open("cbdaylog.txt", "w")
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        #pandas.set_option('display.height', 1500)
        pandas.set_option('display.max_rows', 1500)
        self.dataPath = "../data/"
        self.resultPath = "../result/"
        self.strategyPath = "../strategy/"
        self.screenPath = "../screen/"
        self.pid = 0 #dow30=0,focus=1
        self.nmuBest = 3 # 3 best result
        self.tradesup = tradesupport.Trade(self)
        self.simutable = simutable.SimuTable(self)
        self.mkt = marketdata.MarketData()
        
    # google style portfolio file    
    '''
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
    def loadSymbolListFile(self,fileName, pid):
        table = self.mkt.loadSymbolLstFilePid(fileName,pid)
        #print table
        stocklist = table.values.tolist()
        return stocklist
        
    def getTradeSupport(self):
        return self.tradesup

    def getSimuTable(self):
        return self.simutable
        
    def getDataPath(self):
        return self.dataPath

    def getResultPath(self):
        return self.resultPath

    def getNumBest(self):
        return self.nmuBest        
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' -p <chart=1,mode=1> -g <strategy> -s 2010-01-01 -e 2014-12-30"
        print "optimization:run backtest.py -t aapl -p 'chart=1&mode=1' -g st_quotient -s 2010-01-01 -e 2015-01-05"
        print "run backtest.py -t xom -p 'chart=1&mode=0' -g st_aeoas -s 2010-01-01 -e 2015-01-05"
        print "=== Optimization ==============================================="
        print "optimize single stock:"
        print "\trun backtest.py -t intc -p 'chart=0&mode=1' -g st_aeoas -s 2014-01-01 -e 2015-01-15"
        print "optimize portfolio:"
        print "\trun backtest.py -f ..\data\portfolio2015.txt -p 'chart=0&mode=1' -g st_aeoas -s 2013-12-20 -e 2015-01-15"
        
        print "strategy batch:run backtest.py -b strategylist.txt"
        print "example:run backtest.py -t aapl -p 'chart=1&mode=0&k1=0.7&k2=0.4&cl=25' -g st_quotient -s 2010-01-01 -e 2015-01-05"
        print "example:run backtest.py -t aapl -p 'chart=1&mode=0&k1=0.7&k2=0.4&cl=25' -g stc_quomv -s 2010-01-01 -e 2015-01-05"

                    
    def parseOption(self):
        self.startdate="2010-1-1"
        self.enddate= datetime.datetime.now().strftime("%Y-%m-%d")
        self.ticklist=[]
        self.strategy=""
        ret=False
        # symbol list file
        symbolFile = ""
        pid=0 # default = 0
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:g:s:e:p:b:i:", \
                ["filename", "ticklist","strategy","startdate","enddate","parameter","pid"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                symbolFile = arg
            elif opt in ("-t", "--ticklist"):
                #newstr = arg.replace("'", "")                
                self.ticklist = arg.split(",")
            elif opt in ("-b", "--strategybatch"):
                ret = self.loadStrategyBatchCfg(arg)                
            elif opt in ("-g", "--strategy"):
                self.strategyName  = arg
            elif opt in ("-s", "--startdate"):
                self.startdate = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
            elif opt in ("-p", "--parameter"):
                self.parameter = self.parseParam(arg)
            elif opt in ("-i", "--pid"):
                pid = int(arg)    
        self.hasChart = False
        
        if symbolFile!="":
            self.ticklist = self.loadSymbolListFile(symbolFile,self.pid)
            print "processing tick:",self.ticklist
            #sys.exit()
        if 'chart' in self.parameter:
            if self.parameter['chart']=='1':
                self.hasChart = True
                print "enable chart"
                
        if not ret:            
            if (not self.ticklist) or (self.strategyName==""):
                self.usage()
                sys.exit()
            
    #parse parameter str: k1=0.9,k2=0.4,cl=30
    # return param dict
    def parseParam(self,arg):
        param = {}
        #newstr = arg.replace("'", "")   
        newstr=re.sub('[ \'"]','',arg)
        for item in newstr.split('&'):
            key,value = item.split('=')
            param[key] = value  
        return param
            
    def createStrategy(self,filename):
        #__import__(filename)
        #strategy = getattr(sys.modules[filename], filename)
        module_meta = __import__(filename, globals(), locals(), [filename])
        print module_meta
        c = getattr(module_meta, filename) 
        myobject = c(self)
        print "created strategy=",filename
        #add strategy to trade order decision matrix
        self.tradesup.addStrategy(myobject.getStrategyName())
        
        #strategy name
        self.simutable.setName(filename)
        return myobject
        
    ############################################################################
    # strategy batch
    ############################################################################
    # load into strategy, strategy_result_file
    def loadStrategyBatchCfg(self,fileName):
        fileName = self.dataPath + fileName
        fp = open(fileName,'r',-1)
        for line in fp:         
            name,file = line.split('=')
            if name[0]!='#':
                self.stgyBatchCfg.append({name,file})
                print "add strategy=",name
        fp.close()
        return True
    
    #file name format:st_quotient_best_2015-01-10.csv  
    def parseStrategyResult(self):
        '''
        self.stgyBatch={} # [{name,file},{}]
        for stname,stfileprefix in self.stgyBatchCfg:
            pattern = self.resultPath+stfileprefix+'*'
            datePattern = self.resultPath+stfileprefix+'_%Y-%m-%d.csv'
            latest = datetime.datetime(1990,1,1)
            newestFile = ""
            for fn in glob.glob(pattern):
                # extract date
                d = datetime.datetime.strptime(fn, datePattern)
                if d>latest:
                    latest=d
                    newestFile = fn
            self.stgyBatch[stname] = newestFile
        '''
        # match the exact file name
        self.stgyBatch={} # [{name,file},{}]
        for stname,stfilename in self.stgyBatchCfg:
            fn = self.dataPath + stfilename
            self.stgyBatch[stname] = fn
        return 
        
    def runStrategyBatch(self):
        self.hasChart = False
        tick2StgyBatch = {}
        batchrept = testreport.TestReport(self)
        batchrept.setup(self.getBenchmarkPx())
        for stkey in self.stgyBatch:           
            fileName = self.stgyBatch[stkey]
            fp = open(fileName,'r',-1)
            fp.readline() # skip first line
            for line in fp:         
                items = line.split(',')
                symbol = items[1] #symbol
                param = items[2]
                if not symbol in tick2StgyBatch:
                    stgyParam = {}
                    tick2StgyBatch[symbol] = stgyParam
                else:
                    stgyParam = tick2StgyBatch[symbol]
                stgyParam[stkey] = param
                    
            fp.close()
            
        stgySet = ["%s\n" % item  for item in self.stgyBatch]
        print "strategy = ", stgySet 
            
        
        
        # strategy instance mapping
        print self.startdate, self.enddate
        stgyInstx = {}
        for tick in tick2StgyBatch:            
            stgyParam =  tick2StgyBatch[tick]
            # download
            try:
                tickOhlcPx = web.get_data_yahoo(tick, self.startdate, self.enddate) #startdate
            except:
                # IO error
                print "System/Network Error when retrieving ",tick," skip it"
                continue
            tickOhlcPx = self.convert2AdjPrice(tickOhlcPx)
            
            for stgyName in stgyParam:
                if not stgyName in stgyInstx:
                    #create strategy
                    stgy = self.createStrategy(stgyName)
                    stgyInstx[stgyName] = stgy
                else:
                    stgy = stgyInstx[stgyName]
                    
                paramstr = stgyParam[stgyName]
                #print stgy,param
                param = self.parseParam(paramstr)
                
                stgy.setupParam(param)
                stgy.runStrategy(tick, tickOhlcPx)                
                batchrept.addTestResult(tick, stgyName, paramstr, self.tradesup.getDailyValue(), stgy.getMoreInfo())
                    
        batchrept.createTestReport(self.startdate, self.enddate)
        return 
    
    
    ###########################################################################
    # main routine
    ###########################################################################        
    #[backtest] strategy protfolio startdate enddate
    def process(self):       
        self.parseOption() 
        if len(self.stgyBatchCfg)>0:
           self.parseStrategyResult()
           self.runStrategyBatch()
        else:   
            strategy = self.createStrategy(self.strategyName)
            self.startTest(strategy)

    def convert2AdjPrice(self,df):
        ratio=1.
        for index, row in df.iterrows():        
            if row['Close']!=row['Adj Close']:
                ratio=row['Adj Close']/row['Close']
                df.loc[index,'Close']=df.loc[index,'Close']*ratio
                df.loc[index,'Open']=df.loc[index,'Open']*ratio
                df.loc[index,'High']=df.loc[index,'High']*ratio
                df.loc[index,'Low']=df.loc[index,'Low']*ratio
        return df
        
    def getBenchmarkPx(self):
        try:
            benchmark_px = web.get_data_yahoo("spy", self.startdate, self.enddate)['Adj Close']
        except:
            # IO error
            print "System/Network Error when retrieving benchmark price, skip it"
        return benchmark_px
        
    def startTest(self,strategy):
        #prepare data
        all_data = {}
        firstTick=False
        #stRet = True
        if self.parameter['mode']=='1':
            mode = 1 #optimizer
        else:
            mode = 0 #normal
        self.tradesup.setMode(mode)
        
        #benchmark_px is series?
        try:
            benchmark_px = web.get_data_yahoo("spy", self.startdate, self.enddate)['Adj Close']
            

        except:
            # IO error
            print "System/Network Error when retrieving benchmark price, skip it"
        
        if self.hasChart==True:
            self.setupChart()
            
        
        for ticker in self.ticklist:
            # retrieve data
            try:
                print "processing ",ticker
                all_data[ticker] = web.get_data_yahoo(ticker, self.startdate, self.enddate)
            except:
                # IO error
                print "System/Network Error when retrieving ",ticker," skip it"
                continue
            all_data[ticker] = self.convert2AdjPrice(all_data[ticker])
            if firstTick==False:
                sdate = all_data[ticker].index        
                self.sdatelabel = sdate.to_pydatetime()

            self.tradesup.beginStrategy(ticker, strategy.getStrategyName())
            # run strategy
            ohlc_px = all_data[ticker]
            self.simutable.setupSymbol(ticker,benchmark_px)
            if mode == 1: #optimizer
                strategy.runOptimization(ticker, ohlc_px, benchmark_px)
                self.simutable.procSimuReportnAddBestReport()                
                self.tradesup.setDailyValueDf(self.simutable.getBestDv())
        
            else: #normal
                strategy.runStrategy(ticker, ohlc_px, self.parameter)
                self.simutable.procSimuReportnAddBestReport(False)  
                
            self.tradesup.endStrategy()

                
            dv = self.tradesup.getDailyValue()
            if firstTick==False:
                if self.hasChart==True:
                    firstTradeIdx = self.tradesup.getFirstTradeIdx()
                    firstTradeDate = self.tradesup.getFirstTradeDate()
                    dforders = self.tradesup.getTradeReport()
                    #print "first trade info idx=",firstTradeIdx," date=",firstTradeDate
                    self.drawChart(ticker,ohlc_px['Adj Close'],self.strategyName,dv['dayvalue'],firstTradeIdx,dforders)
                firstTick=True
                
        ####################################################
        # end of for loop 
        ####################################################
        #if mode == 1:  
        self.simutable.makeBestReport()            
            
        if self.hasChart==True:
            self.drawBenchMark(benchmark_px, firstTradeIdx, firstTradeDate)
            
        '''else:
            if self.hasChart==True:
                self.closeChart()
        '''
                
        #only print trade log when only one tick                 
        if len(self.ticklist) == 1:
            #print "\n"
            #print "== BEST TRADE REPORT ==========================================="
            print self.tradesup.getTradeLogDetail()
            #self.printTradeReport()
                
    '''def printTradeReport(self):
        # print trade report
        dforders = self.tradesup.getTradeReport()
        print "\n"
        print "== BEST TRADE REPORT ==========================================="
        perfdata = dforders['pnl'].sum()
        bhprofit = self.tradesup.getBHprofit() #buy&hold profit
        print dforders,"PnL=",perfdata,"B/H profit=",bhprofit
    '''            
    def closeChart(self):
        plt.close(self.fig)
        
    def setupChart(self):
        left, width = 0.1, 0.8
        rect1 = [left, 0.75, width, 0.2]
        rect2 = [left, 0.1, width, 0.65]  #lower left = 0.1,0.1, upper right = 0.9,0.75
        #rect3 = [left, 0.1, width, 0.2]
        self.fig = plt.figure(facecolor='white')
        axescolor  = '#f6f6f6'  # the axes background color
        self.ax1 = self.fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
        self.ax2 = self.fig.add_axes(rect2, axisbg=axescolor, sharex=self.ax1)
        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)        
        plt.setp(self.ax1.get_xticklabels(), visible=False)
        self.perftxt=""
         #ax2.yaxis.label.set_color("w")
        self.ax2.spines['bottom'].set_color("#5998ff")
        self.ax2.spines['top'].set_color("#5998ff")
        self.ax2.spines['left'].set_color("#5998ff")
        self.ax2.spines['right'].set_color("#5998ff")
        

    #draw benchmark curve,offset=firstTradeIdx
    def drawBenchMark(self,benchmark_px,firstDateOffset,firstTradeDate):
        textsize = 9
        bm_offset=benchmark_px.index.get_loc(firstTradeDate)
        
        bm_returns = benchmark_px[bm_offset:].pct_change()
        bmret_index = (1+bm_returns).cumprod()
        #print "drawBenchMark,len(bm)",len(bmret_index) #firstTradeDate,bm_offset
        bmret_index[0] = 1
        #print offset,len(self.sdatelabel[offset:]),len(bmret_index),len(bm_returns),len(benchmark_px)
        
        self.ax2.plot(self.sdatelabel[firstDateOffset:],bmret_index,label='benchmark')        
        self.ax2.text(0.55, 0.95, self.perftxt, horizontalalignment='left',transform=self.ax2.transAxes, fontsize=textsize)
        
        #draw legend at upper left
        legend = self.ax2.legend(loc='upper left', shadow=True)        
        # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
        frame = legend.get_frame()
        frame.set_facecolor('0.90')
        

        ylim = self.ax2.get_ylim()
        self.ax2.set_ylim([ylim[0]-0.5,ylim[1]+0.5]);

        plt.show()
        return
    
    # draw pnl vs benchmark curve ,offset=
    def drawChart(self,symbol,close_px,stgy_name,strgy_ret,offset,dforders):
        px_returns = close_px[offset:].pct_change()
        pxret_index = (1+px_returns).cumprod()
        pxret_index[0] = 1
        sgy_returns = strgy_ret[offset:].pct_change()
        sgyret_index = (1+sgy_returns).cumprod()
        sgyret_index[0] = 1        
        stgy_name = stgy_name+"_"+symbol        

        perftxt = " %s:%.2f %s:%.2f" %(symbol,pxret_index.iloc[-1],stgy_name,sgyret_index.iloc[-1])
        self.perftxt += perftxt
        print "chart start at", self.sdatelabel[offset] 
        self.ax2.plot(self.sdatelabel[offset:],pxret_index,label=symbol)
        self.ax2.plot(self.sdatelabel[offset:],sgyret_index,label=stgy_name)
        self.ax2.grid(True, color='w')
        self.ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
        self.ax2.yaxis.set_major_locator(mticker.MaxNLocator(10))
        
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax2.yaxis.label.set_color("b")
        
        ########################################################################
        # buy / sell orders annotation
        '''dforders = self.tradesup.getTradeReport()
        print "\n"
        print "== BEST TRADE REPORT ==========================================="
        perfdata = dforders['pnl'].sum()
        bhprofit = self.tradesup.getBHprofit() #buy&hold profit
        print dforders,"PnL=",perfdata,"B/H profit=",bhprofit'''
        if len(dforders.index)==0:
            return
        
        for row_index, row in dforders.iterrows():
            date = row_index

            ordertxt = "%s@\n%.2f"%(row['order'],row['price'])
            if row['order']!="buy":
                ordertxt+=('\np/l=\n%.2f'%row['pnl'])            
            
            oriyxis = sgyret_index.asof(date)
            
            if row['order']=='buy':                
                self.ax2.annotate(ordertxt, xy=(date, oriyxis + 0.1),
                xytext=(date, oriyxis+0.3),                
                arrowprops=dict(facecolor='black'),
                horizontalalignment='left', verticalalignment='top')
            else:                
                self.ax2.annotate(ordertxt, xy=(date, oriyxis - 0.1),
                xytext=(date, oriyxis - 0.3),
                arrowprops=dict(facecolor='green'),
                horizontalalignment='left', verticalalignment='top')
        return
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    bt = BackTest()
    bt.process()
    #process(sys.argv[1:],None)