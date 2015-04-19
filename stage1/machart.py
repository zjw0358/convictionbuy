'''
masterchart
- display equity chart

use case:    
run masterchart -t "vmw"

'''
import getopt
import sys
import datetime
import pandas.io.data as web
import pandas
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import OrderedDict
import ms_reuter

class MasterChart:
    def __init__(self):
        self.enddate = ""
        self.startdate = ""
        self.reuter = ms_reuter.ms_reuter()
        return
        
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

        if not self.ticklist:
            print "ticklist is empty"
            self.usage()
            sys.exit()
        print "start date", self.startdate
        print "end date", self.enddate
        #print "portfolio id mask ",self.pid
        print "=========================="

    #usage
    def usage(self):
        print "run machart.py -t aapl.o"
     
    ''' 
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
        plt.show()
    # draw pnl vs benchmark curve ,offset=
    def drawChart(self,symbol,ohlc):
        sdate = ohlc.index        
        sdatelabel = sdate.to_pydatetime()
        print sdatelabel      
        #perftxt = " %s:%.2f %s:%.2f" %(symbol,pxret_index.iloc[-1],stgy_name,sgyret_index.iloc[-1])
        #self.perftxt += perftxt
        #print "chart start at", self.sdatelabel[offset] 
        
        self.ax2.plot(sdatelabel,ohlc['Adj Close'],label=symbol)
        #ohlc['Adj Close'].plot(ax=self.ax2,style='k-')
        #self.ax2.plot(self.sdatelabel[offset:],sgyret_index,label=stgy_name)
        self.ax2.grid(True, color='w')
        #self.ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
        #self.ax2.yaxis.set_major_locator(mticker.MaxNLocator(10))
        
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax2.yaxis.label.set_color("b")
    '''   
    def drawCompChart(self,df):
        fig = plt.figure(facecolor='white')
        ax = fig.add_subplot(1, 1, 1)
        df.plot(ax=ax,color=['r', 'g', 'b', 'r', 'g', 'b', 'r'])
        plt.show()
        return
    # resample stock eps with date index
    def resampleEps(self,symbol,endDate):
        table = pandas.DataFrame([symbol.upper()],columns=['symbol'])
        param = OrderedDict()
        param['$eps']=""
        df = self.reuter.process(table,param)
        df.drop('symbol', axis=1, inplace=True) #drop symbol column
        df = pandas.melt(df) 
        df.drop('variable',axis=1,inplace=True) #drop variable column 'epsq1e,epsqtr0...'
        df[df == 0.000] = numpy.nan 
        start = -len(df.index)-1
        print start,df
        df = pandas.rolling_sum(df.iloc[:start:-1], 4, min_periods=4) # rolling window = 4 (quarter)
        df = df.dropna()
        print df
        lst =df['value'].values.tolist()
        lst.insert(0,lst[0])
        
        frame = pandas.DataFrame(lst,index=pandas.date_range(end=endDate, periods=len(lst), freq='Q'),columns=['eps'])        
        frame = frame.resample('D',fill_method='bfill')  #backward filling
        lasteps = lst[-1]
        startday = frame.index[-1].to_pydatetime() + datetime.timedelta(days=1)
        startDate = startday.strftime("%Y-%m-%d")
        frame2 = pandas.DataFrame(lasteps,index=pandas.bdate_range(start=startDate,end=endDate, freq='D'),columns=['eps'])
        #print frame2
        #print frame
        #frame = pandas.merge(frame,frame2,left_index=True,right_on=True,how='outer')
        #frame = frame.join(frame2,how='outer')
        #frame = frame.merge(frame2,left_index=True,right_index=True,on='eps')
        frame = frame.append(frame2)
        print frame
        return frame
                        
    def process(self):
        self.parseOption()
        for tick in self.ticklist:
            symbol=tick.upper()
            lf = self.resampleEps(symbol,self.enddate)
            startDate = lf.index[0].to_pydatetime().strftime("%Y-%m-%d")
            try:
                ohlc = web.get_data_yahoo(symbol, startDate, self.enddate)
                rf = ohlc['Adj Close']
            except:
                print "System/Network Error when retrieving ",symbol," skip it"
       
            mf = lf.join(rf)
            mf = mf.dropna()
            mf['pe'] = mf['Adj Close']/mf['eps']
            mf = mf.pct_change()
            mf = (1+mf).cumprod()
            print mf
            self.drawCompChart(mf)
            
if __name__ == "__main__":
    obj = MasterChart()
    obj.process()
 