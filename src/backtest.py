import pandas.io.data as web
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
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
        '''drawChart(sdatelabel,spy_px,close_px,df['dayvalue'],offset)
        strategy.drawChart(ax1,sdatelabel)'''
        
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
        print "Sharpe %.2f " % (getSharpe(df['dayvalue'][offset:])) #,sdatelabel[offset:]

# beta
'''def getBeta2(sra,srm):
    bm_returns = srm.pct_change()
    sgy_returns = sra.pct_change()
    bm_returns=bm_returns.dropna()
    sgy_returns=sgy_returns.dropna()
    
    covariances = np.cov(sgy_returns, bm_returns)
    print "beta2",covariances
    return np.mean(covariances) / np.var(srm) wrong'''

def getBeta(bm_returns,sgy_returns):
    '''bm_returns = srm.pct_change()
    sgy_returns = sra.pct_change()
    bm_returns=bm_returns.dropna()
    sgy_returns=sgy_returns.dropna()'''
    #print type(bm_returns)
    #print bm_returns
    #print sgy_returns
    
    covmat = np.cov(bm_returns,sgy_returns)
    print "beta1",covmat
    beta = covmat[0,1]/covmat[1,1]
    return beta
    
def basefacts(bm_returns,sgy_returns):
    covmat = np.cov(bm_returns,sgy_returns)

    beta = covmat[0,1]/covmat[1,1]
    alpha = np.mean(sgy_returns)-beta*np.mean(bm_returns)
    
    
    ypred = alpha + beta * bm_returns
    SS_res = np.sum(np.power(ypred-sgy_returns,2))
    SS_tot = covmat[0,0]*(len(bm_returns)-1) # SS_tot is sample_variance*(n-1)
    r_squared = 1. - SS_res/SS_tot
    # 5- year volatiity and 1-year momentum
    volatility = np.sqrt(covmat[0,0])
    momentum = np.prod(1+sgy_returns.tail(12).values) -1
    
    # annualize the numbers
    prd = 12. # used monthly returns; 12 periods to annualize
    alpha = alpha*prd
    volatility = volatility*np.sqrt(prd) 
    print beta,alpha, r_squared, volatility, momentum      
    
#alpha
def getAlpha(beta,bm_returns,strgy_returns):
    return np.mean(strgy_returns)-beta*np.mean(bm_returns)
   
# sharpe
def getSharpe(dayvalue):
     daily_rets = dayvalue.pct_change()
     daily_sr = lambda x:x.mean()/x.std()
     compound = lambda x:(1+x).prod()-1
     #print "daily return"
     #for index in range(0, len(daily_rets)):
     #   print index,sdatelabel[index],daily_rets.iloc[index],dayvalue.iloc[index]
     #returns = daily_rets.resample('1B',how=compound)
     return daily_sr(daily_rets)*np.sqrt(252)
# max drawdown    
def maxdd(ser):
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
    #return min(0, cur_dd.min())    
    
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