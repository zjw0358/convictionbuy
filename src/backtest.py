

import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

import sys
import getopt

#from datetime import datetime
import simutable
import tradesupport
import matplotlib.pyplot as plt
import pandas.io.data as web
import pandas
import datetime



   
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
        self.support = tradesupport.Trade()
        self.simutable = simutable.SimuTable(self.support)
        self.parameter={}
        #default log to file, unless specified in parameter
        #sys.stdout = open("cbdaylog.txt", "w")
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)


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
                    
        return stocklist

    def getTradeSupport(self):
        return self.support

    def getSimuTable(self):
        return self.simutable
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' -p <chart=1,mode=1> -g <strategy> -s 2010-01-01 -e 2014-12-30"
        print "example:run backtest.py -t aapl -p 'chart=1,mode=0,k1=0.7,k2=0.4,cf=25' -g st_quotient -s 2010-01-01 -e 2015-01-05"
        print "example:run backtest.py -t aapl -p 'chart=1,mode=0,k1=0.7,k2=0.4,cf=25' -g stc_quomv -s 2010-01-01 -e 2015-01-05"

                    
    def parseOption(self):
        self.startdate="1990-1-1"
        self.enddate= datetime.datetime.now().strftime("%Y-%m-%d")
        self.ticklist=[]
        self.strategy=""
        
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:g:s:e:p:", ["filename", "ticklist","strategy","startdate","enddate","parameter"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.ticklist = self.loadPortfolioFile(arg)
            elif opt in ("-t", "--ticklist"):
                newstr = arg.replace("'", "")                
                self.ticklist = newstr.split()
                
            elif opt in ("-g", "--strategy"):
                self.strategyName  = arg
            elif opt in ("-s", "--startdate"):
                self.startdate = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
            elif opt in ("-p", "--parameter"):
                newstr = arg.replace("'", "")   
                for item in newstr.split(','):
                    key,value = item.split('=')
                    self.parameter[key]=value
        self.hasChart = False
        
        if 'chart' in self.parameter:
            if self.parameter['chart']=='1':
                self.hasChart = True
                print "enable chart"
                            
        if (not self.ticklist) or (self.strategyName==""):
            self.usage()
            sys.exit()
            
    def createStrategy(self,filename):
        #__import__(filename)
        #strategy = getattr(sys.modules[filename], filename)
        module_meta = __import__(filename, globals(), locals(), [filename])
        print module_meta
        c = getattr(module_meta, filename) 
        myobject = c(self)
        
        #strategy name
        self.simutable.setName(filename)
        return myobject
                
    #[backtest] strategy protfolio startdate enddate
    def process(self):
        self.parseOption()          
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
        
    def startTest(self,strategy):
        #prepare data
        all_data = {}
        #initialDeposit = 100000
        

        saveDate=False
        for ticker in self.ticklist:
            try:
                all_data[ticker] = web.get_data_yahoo(ticker, self.startdate, self.enddate)
            except:
                # IO error
                print "System/Network Error when retrieving ",ticker," skip it"
                continue
            all_data[ticker] = self.convert2AdjPrice(all_data[ticker])
            if saveDate==False:
                sdate = all_data[ticker].index        
                self.sdatelabel = sdate.to_pydatetime()
                saveDate = True
                

        #benchmark_px is series?
        benchmark_px = web.get_data_yahoo("spy", self.startdate, self.enddate)['Adj Close']
        if self.hasChart==True:
            self.setupChart()
            
        bm_offset = 0
        for ticker in self.ticklist:
            #print all_data[ticker]
            #close_px = all_data[ticker]['Adj Close']
            ohlc_px = all_data[ticker]
            
            dv = strategy.process(self,ticker,self.parameter,ohlc_px,benchmark_px)
            firstTradeIdx = self.support.getFirstTradeIdx()            
            if bm_offset==0 or firstTradeIdx<bm_offset:
                bm_offset = firstTradeIdx
          
            #print self.strategyName
            #print dv['dayvalue']
            #print firstTradeIdx  
            if self.hasChart==True:
                self.drawChart(ticker,ohlc_px['Adj Close'],self.strategyName,dv['dayvalue'],firstTradeIdx)
            
        self.simutable.makeBestReport()

        if self.hasChart==True:
            self.drawBenchMark(benchmark_px,bm_offset)         

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
        

    #draw benchmark curve
    def drawBenchMark(self,benchmark_px,offset):
        textsize = 9
        bm_returns = benchmark_px[offset:].pct_change()
        bmret_index = (1+bm_returns).cumprod()
        bmret_index[offset] = 1
        
        self.ax2.plot(self.sdatelabel[offset:],bmret_index,label='benchmark')        
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
    
    # draw pnl vs benchmark curve 
    def drawChart(self,symbol,close_px,stgy_name,strgy_ret,offset):
        #plt.rc('axes', grid=True)
        #plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
        
        #textsize = 9
    
        #ax2t = ax2.twinx()
        #ax3  = fig.add_axes(rect3, axisbg=axescolor, sharex=ax1)
        #plt.setp(ax1.get_xticklabels(), visible=False)
        #plt.setp(ax3.get_xticklabels(), visible=False)
        #plt.setp(ax2t.get_xticklabels(), visible=False)
            
        #ax1
        px_returns = close_px[offset:].pct_change()
        pxret_index = (1+px_returns).cumprod()
        pxret_index[offset] = 1
        
        #print type(pxret_index.iloc[-1])
        #print pxret_index
        
        sgy_returns = strgy_ret[offset:].pct_change()
        sgyret_index = (1+sgy_returns).cumprod()
        sgyret_index[offset] = 1
        
        stgy_name = stgy_name+"_"+symbol
        

        
        #lastPctStr = "benchmark:%.2f,portfolio:%.2f,strategy:%.2f" %(bmret_index.iloc[-1],pxret_index.iloc[-1],sgyret_index.iloc[-1])
        #ax2.text(0.55, 0.95, lastPctStr, horizontalalignment='left',transform=ax2.transAxes, fontsize=textsize) 
        perftxt = " %s:%.2f %s:%.2f" %(symbol,pxret_index.iloc[-1],stgy_name,sgyret_index.iloc[-1])
        self.perftxt += perftxt
        
        #ax2.text(0.025, 0.95, lastPctStr, verticalalignment='top',transform=ax2.transAxes, fontsize=textsize)
    
        #ax2.plot(sdatelabel[offset:],bmret_index,label='benchmark')
        self.ax2.plot(self.sdatelabel[offset:],pxret_index,label=symbol)
        self.ax2.plot(self.sdatelabel[offset:],sgyret_index,label=stgy_name)
        self.ax2.grid(True, color='w')
        self.ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
        self.ax2.yaxis.set_major_locator(mticker.MaxNLocator(10))
        
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax2.yaxis.label.set_color("b")
        
        # buy / sell orders annotation
        dforders = self.support.getTradeReport()
        if len(dforders.index)==0:
            return
        prevbuyyxis = 0
        prevsellyxis = 0
        prevselldate = dforders.index[0]
        prevbuydate = dforders.index[0]
        
        #saveOldDate=False
        for row_index, row in dforders.iterrows():
            date = row_index

            #away = 0.2 # make text not overlapped
            ordertxt = "%s@%.2f"%(row['order'],row['price'])
            if row['order']!="buy":
                ordertxt+=('\np/l=%.2f'%row['pnl'])            
            
            oriyxis = sgyret_index.asof(date)
            

                
            if row['order']=='buy':
                '''buycount+=1
                if (buycount%2)==0:
                    away=0.'''

                newyxis = oriyxis + 0.3;
                
                '''if abs(newyxis - prevbuyyxis)<0.2:
                    newyxis = oriyxis+0.2
                prevbuyyxis = newyxis'''
                
                self.ax2.annotate(ordertxt, xy=(date, oriyxis + 0.1),
                xytext=(date, newyxis),                
                arrowprops=dict(facecolor='black'),
                horizontalalignment='left', verticalalignment='top')
            else:
                datedelta = (date-prevselldate).days
                prevselldate = date

                newyxis = oriyxis - 0.3;
                
                if datedelta<30:
                    if prevbuyyxis!=0:
                        newyxis = prevbuyyxis-0.2
                prevbuyyxis = newyxis
                
                self.ax2.annotate(ordertxt, xy=(date, oriyxis - 0.1),
                xytext=(date, newyxis),
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