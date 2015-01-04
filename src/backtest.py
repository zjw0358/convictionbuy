import pandas.io.data as web
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import datetime
import sys
import getopt


import simutable
import tradesupport


left, width = 0.1, 0.8
rect1 = [left, 0.7, width, 0.2]
rect2 = [left, 0.3, width, 0.4]
rect3 = [left, 0.1, width, 0.2]
fig = plt.figure(facecolor='white')
axescolor  = '#f6f6f6'  # the axes background color
ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)

def drawChart(sdatelabel,benchmark_px,close_px,strgy_ret,offset):
    plt.rc('axes', grid=True)
    plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
    
    textsize = 9
  
    #ax2t = ax2.twinx()
    #ax3  = fig.add_axes(rect3, axisbg=axescolor, sharex=ax1)
    plt.setp(ax1.get_xticklabels(), visible=False)
    #plt.setp(ax3.get_xticklabels(), visible=False)
    #plt.setp(ax2t.get_xticklabels(), visible=False)
        
    #ax1
    px_returns = close_px[offset:].pct_change()
    pxret_index = (1+px_returns).cumprod()
    pxret_index[offset] = 1
    
    sgy_returns = strgy_ret[offset:].pct_change()
    sgyret_index = (1+sgy_returns).cumprod()
    sgyret_index[offset] = 1

    bm_returns = benchmark_px[offset:].pct_change()
    bmret_index = (1+bm_returns).cumprod()
    bmret_index[offset] = 1       
    
    
    
    ### plot the price and volume data
    #print "offset=",offset
    #print pxret_index[offset:]
    #print sgyret_index[offset:]
    '''print type(sgyret_index)
    print type(bmret_index)
    print type(pxret_index)
    print bmret_index[-1]
    print pxret_index[-1]
    print sgyret_index.iloc[-1]
    print "dump"
    lastPctStr="price"'''
    lastPctStr = "benchmark:%.2f,portfolio:%.2f,strategy:%.2f" %(bmret_index.iloc[-1],pxret_index.iloc[-1],sgyret_index.iloc[-1])
    #ax2.text(0.025, 0.95, lastPctStr, verticalalignment='top',transform=ax2.transAxes, fontsize=textsize)

    ax2.plot(sdatelabel[offset:],bmret_index,label='benchmark')
    ax2.plot(sdatelabel[offset:],pxret_index,label='portfolio')
    ax2.plot(sdatelabel[offset:],sgyret_index,label='strategy')
    
    ax2.grid(True, color='w')
    ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(8))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.yaxis.label.set_color("b")
    #bottom left = 0,0; upper right = 1,1
    ax2.text(0.55, 0.95, lastPctStr, horizontalalignment='left',transform=ax2.transAxes, fontsize=textsize)    
    
 
    #ax2.yaxis.label.set_color("w")
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")

    #legend
    # draw at right side
    #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    
    #draw at upper left
    legend = ax2.legend(loc='upper left', shadow=True)
    
    # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
    frame = legend.get_frame()
    frame.set_facecolor('0.90')
    plt.show()


def startTest(strategy,symlst,startdate,enddate):
    #prepare data
    all_data = {}
    initialDeposit = 100000
    
    for ticker in symlst:
        all_data[ticker] = web.get_data_yahoo(ticker, startdate, enddate)
        all_data[ticker] = self.convert2AdjPrice(all_data[ticker])
        #print all_data[ticker]


    spy_px = web.get_data_yahoo("spy", startdate, enddate)['Adj Close']
    
    
    for ticker in symlst:
        #print all_data[ticker]
        close_px = all_data[ticker]['Adj Close']
        ohlc_px = all_data[ticker]
        sdate = all_data[ticker].index        
        sdatelabel = sdate.to_pydatetime()
        #strategy.setup(10000)
        
        df = strategy.processOptimization(ticker,ohlc_px,spy_px)

        '''df = strategy.procMultiData(ohlc_px)#close_px
    
        offset = strategy.getOffset()
        drawChart(sdatelabel,spy_px,close_px,df['dayvalue'],offset)
        strategy.drawChart(ax1,sdatelabel)
        
        #calculation
        bm_returns = spy_px[offset:].pct_change()
        bmret_index = (1+bm_returns).cumprod()
        bmret_index[offset] = 1
        
        sgy_returns = df['dayvalue'][offset:].pct_change()
        sgyret_index = (1+sgy_returns).cumprod()
        sgyret_index[offset] = 1  
        
        px_returns = close_px[offset:].pct_change()
        pxret_index = (1+px_returns).cumprod()
        pxret_index[offset] = 1
        
        #print ohlc_px.index.values
        #print df
        #print spy_px[offset:]
        rtbm = spy_px[offset:].resample('M',how='last')
        rtsgy = df['dayvalue'][offset:].resample('M',how='last')
        
        bm_returns = rtbm.pct_change()
        sgy_returns = rtsgy.pct_change()
        bm_returns=bm_returns.dropna()
        sgy_returns=sgy_returns.dropna()
        
        #print rts.pct_change()
        #print rbts.pct_change()
        #beta2 = getBeta2(bmret_index[offset:],sgyret_index[offset:])
        #beta2 = getBeta2(rts,rbts)
        #beta2 = getBeta2(bmret_index[offset:],pxret_index[offset:])
        #beta = getBeta(bm_returns,sgy_returns)
        #alpha = getAlpha(beta,bm_returns,sgy_returns)
        #print "Beta %.2f " % (beta)
        #print "Alpha %.2f " % (alpha)        
        #print "Beta2 %.2f " % (beta2)
        basefacts(bm_returns,sgy_returns)
        print "Max draw down %.2f %%" % (maxdd(df['dayvalue'][offset:])*100)
        print "Sharpe %.2f " % (getSharpe(df['dayvalue'][offset:])) #,sdatelabel[offset:]'''

# beta
'''def getBeta2(sra,srm):
    bm_returns = srm.pct_change()
    sgy_returns = sra.pct_change()
    bm_returns=bm_returns.dropna()
    sgy_returns=sgy_returns.dropna()
    
    covariances = np.cov(sgy_returns, bm_returns)
    print "beta2",covariances
    return np.mean(covariances) / np.var(srm) wrong'''

'''def getBeta(bm_returns,sgy_returns):
    bm_returns = srm.pct_change()
    sgy_returns = sra.pct_change()
    bm_returns=bm_returns.dropna()
    sgy_returns=sgy_returns.dropna()
    #print type(bm_returns)
    #print bm_returns
    #print sgy_returns
    
    covmat = np.cov(bm_returns,sgy_returns)
    print "beta1",covmat
    beta = covmat[0,1]/covmat[1,1]
    return beta'''
    

   
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
     
     
# max drawdown    
'''def maxdd(ser):
    # only compare each point to the previous running peak
    # O(N)
    running_max = pd.expanding_max(ser)
    #cur_dd = ser - running_max
    ddpct =  (ser - running_max)/running_max
    #print ser
    #for item in running_max.values:
    #for index in range(0, len(running_max)):
    #    print ser[index],running_max[index],ddpct[index]
    return abs(ddpct.min())
    #return min(0, cur_dd.min()'''
    



    


class BackTest:
    def __init__(self):
        self.support = tradesupport.Trade()
        self.simutable = simutable.SimuTable(self.support)
        
    def loadPortfolioFile(self,fileName):
        fp = open(fileName,'r',-1)
        pf = fp.read()
        stocklist = pf.split(',')    
        return stocklist

    def getTradeSupport(self):
        return self.support
    def getSimuTable(self):
        return self.simutable
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' -p <chart=1,mode=1> -g <strategy> -s 2010-01-01 -e 2014-12-30"
                    
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
                self.ticklst = self.loadPortfolioFile(arg)
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
                self.parameter={}
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
        myobject = c()
        
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
        
        try:
            saveDate=False
            for ticker in self.ticklist:
                all_data[ticker] = web.get_data_yahoo(ticker, self.startdate, self.enddate)
                all_data[ticker] = self.convert2AdjPrice(all_data[ticker])
                if saveDate==False:
                    sdate = all_data[ticker].index        
                    self.sdatelabel = sdate.to_pydatetime()
                    saveDate = True
        except:
            # IO error
            print "System/Network Error,exit"
            sys.exit()
                
        #print all_data,type(all_data)
        #return
        #benchmark
        
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
                
            if self.hasChart==True:
                self.drawChart(ticker,ohlc_px['Adj Close'],self.strategyName,dv['dayvalue'],firstTradeIdx)
            
        self.simutable.makeBestReport()

        if self.hasChart==True:
            self.drawBenchMark(benchmark_px,bm_offset)         

    def setupChart(self):
        left, width = 0.1, 0.8
        rect1 = [left, 0.7, width, 0.2]
        rect2 = [left, 0.3, width, 0.4]
        rect3 = [left, 0.1, width, 0.2]
        fig = plt.figure(facecolor='white')
        axescolor  = '#f6f6f6'  # the axes background color
        self.ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
        self.ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)
        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)        
        plt.setp(self.ax1.get_xticklabels(), visible=False)
        self.perftxt=""

    #draw benchmark curve
    def drawBenchMark(self,benchmark_px,offset):
        textsize = 9
        bm_returns = benchmark_px[offset:].pct_change()
        bmret_index = (1+bm_returns).cumprod()
        bmret_index[offset] = 1
        self.ax2.plot(self.sdatelabel[offset:],bmret_index,label='benchmark')
        
        self.ax2.text(0.55, 0.95, self.perftxt, horizontalalignment='left',transform=self.ax2.transAxes, fontsize=textsize)
         
        #draw at upper left
        legend = self.ax2.legend(loc='upper left', shadow=True)
        
        # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
        frame = legend.get_frame()
        frame.set_facecolor('0.90')
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
        
        print type(pxret_index.iloc[-1])
        print pxret_index
        sgy_returns = strgy_ret[offset:].pct_change()
        sgyret_index = (1+sgy_returns).cumprod()
        sgyret_index[offset] = 1
        print type(sgyret_index.iloc[-1])
        print sgyret_index
    
        '''bm_returns = benchmark_px[offset:].pct_change()
        bmret_index = (1+bm_returns).cumprod()
        bmret_index[offset] = 1 '''      
        
        
        
        ### plot the price and volume data
        #print "offset=",offset
        #print pxret_index[offset:]
        #print sgyret_index[offset:]
        '''print type(sgyret_index)
        print type(bmret_index)
        print type(pxret_index)
        print bmret_index[-1]
        print pxret_index[-1]
        print sgyret_index.iloc[-1]
        print "dump"
        lastPctStr="price"'''
        
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
        self.ax2.yaxis.set_major_locator(mticker.MaxNLocator(8))
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax2.yaxis.label.set_color("b")
        #bottom left = 0,0; upper right = 1,1
           
        
    
        #ax2.yaxis.label.set_color("w")
        self.ax2.spines['bottom'].set_color("#5998ff")
        self.ax2.spines['top'].set_color("#5998ff")
        self.ax2.spines['left'].set_color("#5998ff")
        self.ax2.spines['right'].set_color("#5998ff")
    
        #legend
        # draw at right side
        #plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        
        #draw at upper left
        '''legend = ax2.legend(loc='upper left', shadow=True)
        
        # The frame is matplotlib.patches.Rectangle instance surrounding the legend.
        frame = legend.get_frame()
        frame.set_facecolor('0.90')
        plt.show()'''
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    bt = BackTest()
    bt.process()
    #process(sys.argv[1:],None)