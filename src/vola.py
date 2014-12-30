import stockeod
import traceback
import pandas as pd
import numpy as np    
#import datetime
import matplotlib.pyplot as plt
import math


# make it more common?
def queryVolatile(sym,startdate,dbconn):
    
    df=stockeod.getAllDataFrame(sym,startdate,dbconn)
    #df['chg']=pd.Series(np.random.randn(sLength), index=df.index)
    df['chg']=1
    df['lschg']=1
    p1=0.0
    p0=0.0
    for index, row in df.iterrows():
        if index==0:
            df.ix[0,['chg']] = 0
        else:            
            p1 =  df.ix[index,'sadjclose']
            p0 =  df.ix[index-1,'sadjclose']
            pclose = df.ix[index,'sclose']
            plow = df.ix[index,'slow']
            chg = 100*(p1 / p0 - 1)
            #prev_close = pclose / (chg/100+1)
            lschg = abs((plow/pclose-1)*100)
            #print index,plow,prev_close,chg,lschg
            #lschg = lschg - chg
            
                
            #if chg>=0:
            #    chg+=0.4
            #else:
            #    chg-=0.4
                    
            df.ix[index,'chg'] = chg #int(round(chg))
            df.ix[index,'lschg'] = lschg
            
    #print df[['symbol','sdate','sopen','sadjclose','chg','lschg']]
    print df
    #bins = [-1000,-5,-3,-1,1,3,5,1000]
    #cats = pd.cut(df['chg'],bins)
    #cats.plot(kind='kde')
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1)
    ax2 = fig.add_subplot(2,1,2)
    ax1.set_xlim([-20,20])
    mybins=[-15,-5,-3,-1,1,3,5,15]
    
    cats = pd.cut(df['chg'],mybins)
    print "change percent\n", pd.value_counts(cats)
    
    shadowbins=[0,1,3,5,15]
    shadowcats = pd.cut(df['lschg'],shadowbins)
    print "shadow line change percent\n", pd.value_counts(shadowcats)
    df['chg'].hist(ax=ax1,bins=mybins)
    df['chg'].plot(ax=ax1,kind='kde')
    df['lschg'].hist(ax=ax2,bins=shadowbins)
    df['lschg'].plot(ax=ax2,kind='kde')
    plt.show()
    

    #df.plot(ax=ax,style='k')
    
    #tips = pd.read_csv('tips.csv')
    #tips['tip_pct'] = tips['tip'] / tips['total_bill']
    #tips['tip_pct'].hist(bins=50)
    #tips['tip_pct'].plot(kind='kde')
    #print tips
    #print tips
    #print all_data
    #print all_data
def EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2,cutoffLength):
    cutoffLength = 10;
    a1 = math.exp(-math.pi * math.sqrt(2) / cutoffLength);
    coeff2 = 2 * a1 * math.cosh(math.sqrt(2) * math.pi / cutoffLength);
    coeff3 = - a1**2;
    coeff1 = 1 - coeff2 - coeff3;
    filt =  coeff1 * (hp0 + hp1) / 2 + coeff2 * filt1 + coeff3 * filt2;
    return filt

cutoffLength = 20;
k = 0.9;
k2 = 0.4
alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
a1 = math.exp(-1.414 * math.pi / cutoffLength);
b1 = 2 * a1 * math.cos(math.radians(1.414 * 180 / cutoffLength));

def EhlersSuperSmootherFilter2(hp0,hp1,filt1,filt2,cutoffLength):
    '''cutoffLength = 10;'''
    #a1 = math.exp(-1.414 * math.pi / cutoffLength);
    #global a1
    #b1 = 2 * a1 * math.cosh(1.414 * math.pi / cutoffLength);
    
    c2 = b1
    c3 = - a1*a1
    c1 = 1 - c2 - c3;
    filt =  c1 * (hp0 + hp1) / 2 + c2 * filt1 + c3 * filt2;
    return filt
        
def quotient(sym,startdate,dbconn):    
    df=stockeod.getAllDataFrame(sym,startdate,dbconn)

    df['hp']=0.
    df['filt']=0.
    df['nrf']=1.0
    df['quo']=1.0
    df['peak']=0.
    #print type(df.loc[1,'sadjclose'])
    #print df.loc[0,'sadjclose']
    #return
    print "alpha1,",alpha1
    print "a1,",a1
    print "b1,",b1
    #peak1=0.0
    for index, row in df.iterrows():
        if index>=2:
            price = df.loc[index,'sadjclose']
            price1= df.loc[index-1,'sadjclose']
            price2= df.loc[index-2,'sadjclose']
            
            #alpha1 = (math.cosh(math.sqrt(2) * math.pi / 100) + math.sinh (math.sqrt(2) * math.pi / 100) - 1) / math.cosh(math.sqrt(2) * math.pi / 100)
            #alpha1 = (math.cos(0.707*math.pi*2 / 100) + math.sin (0.707*math.pi*2 / 100) - 1) / math.cos(0.707*math.pi*2 / 100)
            hp1 = df.loc[index-1,'hp']
            hp2 = df.loc[index-2,'hp']
            #hp0 = (1 - alpha1 / 2)**2 * (price - 2 * price1 + price2) + 2 * (1 - alpha1) * hp1 - (1 - alpha1)**2 * hp2;
            hp0 = (1 - alpha1 / 2)*(1 - alpha1 / 2) * (price - 2 * price1 + price2) + 2 * (1 - alpha1) * hp1 - (1 - alpha1)*(1 - alpha1) * hp2;
            df.loc[index,'hp'] = hp0
            filt1 = df.loc[index-1,'filt']
            filt2 = df.loc[index-2,'filt'] 
            
            #filt = EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2,cutoffLength);
            filt = EhlersSuperSmootherFilter2(hp0,hp1,filt1,filt2,cutoffLength);
            #fast attack
            peak1 = df.loc[index-1,'peak']
            peak0 = peak1*0.991
            
            af = abs(filt)
            #print type(af),type(filt),type(peak0)
            if af > peak0:
                peak0 = af
            #print index,peak0,peak1
            #peak1 = peak0
            df.loc[index,'peak'] = peak0
            
            NormRoofingFilter = filt / peak0;
            Quotient1 = (NormRoofingFilter + k) / (k * NormRoofingFilter + 1);
            Quotient2 = (NormRoofingFilter + k2) / (k2 * NormRoofingFilter + 1);
            df.loc[index,'quo'] = Quotient1
            df.loc[index,'nrf'] = NormRoofingFilter

    print df
    fig = plt.figure()
    ax1 = fig.add_subplot(2,1,1) 
    ax2 = fig.add_subplot(2,1,2) 
    
    #df['nrf'].plot(ax=ax1)
    df['quo'].plot(ax=ax1)
    rsidata = rsiFunc(df['sadjclose'],14)
    #rsidata.plot(ax=ax2)
    #    date=df['sdate']
    
    ax2.plot(df['sdate'], rsidata)
    
    plt.show()
    
def rsiFunc(prices, n):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100.-100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    
    return rsi
    
def process(args,dbconn):
    cmd = ""
    startdate="1990-1-1"
    if len(args)<1:
        return
        
    
    symbol = args[0]
    if len(args)==2:
        startdate = args[1]
    #queryVolatile(symbol,startdate,dbconn)
    print args

    quotient(symbol,startdate,dbconn)

 




