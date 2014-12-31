import pandas.io.data as web
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
import datetime
import sys

left, width = 0.1, 0.8
rect1 = [left, 0.7, width, 0.2]
rect2 = [left, 0.3, width, 0.4]
rect3 = [left, 0.1, width, 0.2]
fig = plt.figure(facecolor='white')
axescolor  = '#f6f6f6'  # the axes background color
ax1 = fig.add_axes(rect1, axisbg=axescolor)  #left, bottom, width, height
ax2 = fig.add_axes(rect2, axisbg=axescolor, sharex=ax1)

def convert2AdjPrice(df):
    ratio=1.
    for index, row in df.iterrows():        
        if row['Close']!=row['Adj Close']:
            ratio=row['Adj Close']/row['Close']
            df.loc[index,'Close']=df.loc[index,'Close']*ratio
            df.loc[index,'Open']=df.loc[index,'Open']*ratio
            df.loc[index,'High']=df.loc[index,'High']*ratio
            df.loc[index,'Low']=df.loc[index,'Low']*ratio
    return df
                
   
    

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
        all_data[ticker] = convert2AdjPrice(all_data[ticker])
        #print all_data[ticker]


    spy_px = web.get_data_yahoo("spy", startdate, enddate)['Adj Close']
    
    
    for ticker in symlst:
        #print all_data[ticker]
        close_px = all_data[ticker]['Adj Close']
        ohlc_px = all_data[ticker]
        sdate = all_data[ticker].index        
        sdatelabel = sdate.to_pydatetime()
        strategy.setup(100000)
        df = strategy.procMultiData(ohlc_px)#close_px
    
        offset = strategy.getOffset()
        #print df[offset:]
        drawChart(sdatelabel,spy_px,close_px,df['dayvalue'],offset)
        strategy.drawChart(ax1,sdatelabel)
        dd_2(df['dayvalue'])

    
def dd_2(ser):
    # only compare each point to the previous running peak
    # O(N)
    running_max = pd.expanding_max(ser)
    cur_dd = ser - running_max
    #print ser
    #for item in running_max.values:
    for index in range(0, len(running_max)):
        print ser[index],running_max[index]
    
    return min(0, cur_dd.min())    
    
def createStrategy(filename):
    #__import__(filename)
    #strategy = getattr(sys.modules[filename], filename)
    module_meta = __import__(filename, globals(), locals(), [filename])
    print module_meta
    c = getattr(module_meta, filename) 
    myobject = c() 
    return myobject


#[backtest] strategy protfolio startdate enddate
def process(args,dbconn):
    print "backtest args=",args
    startdate="1990-1-1"
    enddate= datetime.datetime.now().strftime("%Y-%m-%d")
    
    if len(args)<2:
        return
        
    filename = args[0]
    symstr = args[1]
    symlst = symstr.split(',')
    print "get stock data:",symlst
    
    if len(args)>=3:
        startdate = args[2]
    if len(args)>=4:
        enddate = args[3]
    
    strategy = createStrategy(filename)
    strategy.config("name","value")
    startTest(strategy,symlst,startdate,enddate)
1
if __name__ == "__main__":
    process(sys.argv[1:],None)