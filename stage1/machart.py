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
import matplotlib.pyplot as plt

class MasterChart:
    def __init__(self):
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

                
    def process(self):
        self.setupChart()
        symbol="aapl"
        try:
            ohlc = web.get_data_yahoo(symbol, self.startdate, self.enddate)
        except:
            print "System/Network Error when retrieving ",symbol," skip it"
        return
if __name__ == "__main__":
    obj = MasterChart()
    obj.process()
 