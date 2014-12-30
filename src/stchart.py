# -*- coding: utf-8 -*-
import pandas.io.data as web
import matplotlib.pyplot as plt

import matplotlib.dates as mdates
import matplotlib.ticker as mticker

import datetime

import quotient


# make it more common?
def drawChart(symlst,startdate,enddate):
    all_data = {}
    mode = 0 # price
    if len(symlst)>1:
        mode = 1 #pct change
        
    for ticker in symlst:
        all_data[ticker] = web.get_data_yahoo(ticker, startdate, enddate)

    

    fig = plt.figure(facecolor='#07000d')
    '''ax1 = plt.subplot2grid((6,4), (1,0), rowspan=4, colspan=4, axisbg='#07000d')
    ax1.grid(True, color='w')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='w')
    plt.ylabel('Stock price and Volume')'''
 
    
    for ticker in symlst:
        close_px = all_data[ticker]['Adj Close']
        print all_data[ticker].index
        sdate = all_data[ticker].index
        if mode==0:
            #close_px.plot(ax=ax1,label=ticker)
            print type(close_px)
            #ax1.plot(sdate.to_pydatetime(),close_px)
        else:
            returns = close_px.pct_change()
            ret_index = (1+returns).cumprod()
            ret_index[0] = 1
            #ret_index.plot(ax=ax1,label=ticker)
            #print close_px
            #print ret_index
        
        #quotient
        ax0 = plt.subplot2grid((6,4), (0,0),  rowspan=1, colspan=4, axisbg='#07000d')#sharex=ax1
        #ax0 = fig.add_subplot(2,1,1)
        #ax2 = fig.add_subplot(2,1,2)
        
        
        
        
        ax0.set_ylim([-1,1])
        sdatelabel = sdate.to_pydatetime()
        quolst = quotient.quotient(close_px,sdatelabel)
        print "date=",len(sdate),"quo=",len(quolst)
        print sdate
        #ax2.plot(sdatelabel[-584:-1], quolst[-584:-1])
        ax0.plot(sdatelabel, quolst)
        posCol = '#386d13'
        negCol = '#8f2020'   
        
        
        ax0.set_yticks([-1,1])
        ax0.yaxis.label.set_color("w")
        ax0.spines['bottom'].set_color("#5998ff")
        ax0.spines['top'].set_color("#5998ff")
        ax0.spines['left'].set_color("#5998ff")
        ax0.spines['right'].set_color("#5998ff")
        ax0.tick_params(axis='y', colors='w')
        ax0.tick_params(axis='x', colors='w')
        plt.ylabel('OnSet')  
        ax0.axhline(1, color=negCol)
        ax0.axhline(-1, color=posCol)
        ax0.axhline(0, color=posCol)
        ax0.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        
        
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()
 

def process(args,dbconn):
    print "chart args=",args
    startdate="1990-1-1"
    enddate= datetime.datetime.now().strftime("%Y-%m-%d")
    if len(args)<1:
        return
        
    #cmd = args[0]
    symstr = args[0]
    symlst = symstr.split(',')
    print "get stock data:",symlst
    if len(args)>=2:
        startdate = args[1]
    if len(args)>=3:
        enddate = args[2]
    
    drawChart(symlst,startdate,enddate)

        
