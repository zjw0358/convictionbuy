

import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

import sys
import getopt

#from datetime import datetime
import simutable
import tradesupport
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
        self.tradesup = tradesupport.Trade()
        self.simutable = simutable.SimuTable(self.tradesup)
        self.parameter = {}
        self.stgyBatchCfg = []
        #default log to file, unless specified in parameter
        #sys.stdout = open("cbdaylog.txt", "w")
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        pandas.set_option('display.height', 1500)
        pandas.set_option('display.max_rows', 1500)
        self.dataPath = "../data/"
        self.resultPath = "../result/"

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

    def getTradeSupport(self):
        return self.tradesup

    def getSimuTable(self):
        return self.simutable
        
    def getDataPath(self):
        return self.dataPath

    def getResultPath(self):
        return self.resultPath
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' -p <chart=1,mode=1> -g <strategy> -s 2010-01-01 -e 2014-12-30"
        print "optimization:run backtest.py -t aapl -p 'chart=1&mode=1' -g st_quotient -s 2010-01-01 -e 2015-01-05"
        print "strategy batch:run backtest.py -b strategylist.txt"
        print "example:run backtest.py -t aapl -p 'chart=1&mode=0&k1=0.7&k2=0.4&cl=25' -g st_quotient -s 2010-01-01 -e 2015-01-05"
        print "example:run backtest.py -t aapl -p 'chart=1&mode=0&k1=0.7&k2=0.4&cl=25' -g stc_quomv -s 2010-01-01 -e 2015-01-05"

                    
    def parseOption(self):
        self.startdate="1990-1-1"
        self.enddate= datetime.datetime.now().strftime("%Y-%m-%d")
        self.ticklist=[]
        self.strategy=""
        ret=False
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:g:s:e:p:b:", ["filename", "ticklist","strategy","startdate","enddate","parameter"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.ticklist = self.loadPortfolioFile(arg)
            elif opt in ("-t", "--ticklist"):
                newstr = arg.replace("'", "")                
                self.ticklist = newstr.split()
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
                
        self.hasChart = False
        
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
            self.stgyBatchCfg.append({name,file})
        fp.close()
        return True
    
    #file name format:st_quotient_best_2015-01-10.csv  
    def parseStrategyResult(self):
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
            
        #print self.stgyBatch
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
                batchrept.addTestResult(tick, stgyName, paramstr, self.tradesup.getDailyValue())
                    
        batchrept.createTestReport()
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
        stRet = True
        
      
        #benchmark_px is series?
        try:
            benchmark_px = web.get_data_yahoo("spy", self.startdate, self.enddate)['Adj Close']
            '''sdate = benchmark_px.index
            self.sdatelabel = sdate.to_pydatetime()'''

        except:
            # IO error
            print "System/Network Error when retrieving benchmark price, skip it"
        
        if self.hasChart==True:
            self.setupChart()
            
        
        for ticker in self.ticklist:
            # retrieve data
            try:
                all_data[ticker] = web.get_data_yahoo(ticker, self.startdate, self.enddate)
            except:
                # IO error
                print "System/Network Error when retrieving ",ticker," skip it"
                continue
            all_data[ticker] = self.convert2AdjPrice(all_data[ticker])
            if firstTick==False:
                sdate = all_data[ticker].index        
                self.sdatelabel = sdate.to_pydatetime()

                
            # run strategy
            ohlc_px = all_data[ticker]            
            ret = strategy.process(self,ticker,self.parameter,ohlc_px,benchmark_px)
            if ret==False: # e.g. parameter mode is not reconginzed
                stRet=False
                continue
            else:
                dv = self.tradesup.getDailyValue()

          
            #print self.strategyName
            #print dv['dayvalue']
            #print firstTradeIdx  
            #print "firstTick=",firstTick,self.hasChart
            if firstTick==False:
                if self.hasChart==True:
                    firstTradeIdx = self.tradesup.getFirstTradeIdx()
                    firstTradeDate = self.tradesup.getFirstTradeDate()
                    print "first trade info idx=",firstTradeIdx," date=",firstTradeDate
                    self.drawChart(ticker,ohlc_px['Adj Close'],self.strategyName,dv['dayvalue'],firstTradeIdx)
                firstTick=True

        if stRet==True:  
            self.simutable.makeBestReport()
            if self.hasChart==True:
                self.drawBenchMark(benchmark_px,firstTradeIdx,firstTradeDate)
        else:
            if self.hasChart==True:
                self.closeChart()

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
        print firstTradeDate,bm_offset
        bm_returns = benchmark_px[bm_offset:].pct_change()
        bmret_index = (1+bm_returns).cumprod()
        bmret_index[bm_offset] = 1
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
    def drawChart(self,symbol,close_px,stgy_name,strgy_ret,offset):
        px_returns = close_px[offset:].pct_change()
        pxret_index = (1+px_returns).cumprod()
        pxret_index[offset] = 1
        
        #print type(pxret_index.iloc[-1])
        #print pxret_index
        
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
        dforders = self.tradesup.getTradeReport()
        print "\n"
        print "== BEST TRADE REPORT ==========================================="
        perfdata = dforders['pnl'].sum()
        bhprofit = self.tradesup.getBHprofit() #buy&hold profit
        print dforders,"PnL=",perfdata,"B/H profit=",bhprofit
        if len(dforders.index)==0:
            return
            
        '''prevbuyyxis = 0
        prevsellyxis = 0
        prevselldate = dforders.index[0]
        prevbuydate = dforders.index[0]'''
        
        #saveOldDate=False
        for row_index, row in dforders.iterrows():
            date = row_index

            #away = 0.2 # make text not overlapped
            ordertxt = "%s@\n%.2f"%(row['order'],row['price'])
            if row['order']!="buy":
                ordertxt+=('\np/l=\n%.2f'%row['pnl'])            
            
            oriyxis = sgyret_index.asof(date)
            
            if row['order']=='buy':
                #newyxis = oriyxis + 0.3;
                
                '''if abs(newyxis - prevbuyyxis)<0.2:
                    newyxis = oriyxis+0.2
                prevbuyyxis = newyxis'''
                
                self.ax2.annotate(ordertxt, xy=(date, oriyxis + 0.1),
                xytext=(date, oriyxis+0.3),                
                arrowprops=dict(facecolor='black'),
                horizontalalignment='left', verticalalignment='top')
                # debug
                #print ordertxt,oriyxis
            else:
                #datedelta = (date-prevselldate).days
                #prevselldate = date
                #newyxis = oriyxis - 0.3;
                
                '''if datedelta<30:
                    if prevbuyyxis!=0:
                        newyxis = prevbuyyxis-0.2'''
                #prevbuyyxis = newyxis
                
                self.ax2.annotate(ordertxt, xy=(date, oriyxis - 0.1),
                xytext=(date, oriyxis - 0.3),
                arrowprops=dict(facecolor='green'),
                horizontalalignment='left', verticalalignment='top')

        #bottom left = 0,0; upper right = 1,1
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    bt = BackTest()
    bt.process()
    #process(sys.argv[1:],None)