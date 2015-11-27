import pandas.io.data as web
import matplotlib.pyplot as plt
import pandas as pd
import chartkit
from scipy.stats.stats import pearsonr 
import numpy as np
from scipy.interpolate import interp1d
import mlpy
import math

def average(x):
    assert len(x) > 0
    return float(sum(x)) / len(x)

def pearson_def(x, y):
    assert len(x) == len(y)
    n = len(x)
    assert n > 0
    avg_x = average(x)
    avg_y = average(y)
    diffprod = 0
    xdiff2 = 0
    ydiff2 = 0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff * ydiff
        xdiff2 += xdiff * xdiff
        ydiff2 += ydiff * ydiff

    return diffprod / math.sqrt(xdiff2 * ydiff2)

class StockChart:
    def __init__(self):
        self.chartkit = chartkit.ChartKit()
        return
    '''
    def calcZigzag(self,df):
        trend = 0 #0-undefined,1-up,-1 down
        lastpx = 0
        lastpx_idx = 0
        zzp = 3
        zzcol = 'zz'
        for index, row in df.iterrows():
            p0 = row['Adj Close']
            if lastpx==0:
                lastpx = p0
                print "first pivot",p0
                df.loc[index,zzcol] = p0
            else:
                chg = (p0/lastpx-1)*100
                #print p0,lastpx,round(chg,2)
                if trend==0:
                    if abs(chg)>zzp:
                        if chg>0:
                            trend = 1
                            print "see up trend",p0
                        else:
                            trend = -1
                            print "see down trend",p0
                        lastpx = p0
                        lastpx_idx = index
                elif trend>0:
                    if chg>0:
                        trend = 1#do nothing
                        lastpx = p0
                        lastpx_idx = index
                    elif chg<0:
                        if abs(chg)>zzp:#pivot point
                            trend = -1
                            print "pivot point",lastpx
                            df.loc[lastpx_idx,zzcol] = lastpx                            
                            print "see down trend",p0
                            lastpx = p0
                            lastpx_idx = index
                elif trend<0:
                     if chg<0:
                         trend = -1#do nothing
                         lastpx = p0
                         lastpx_idx = index
                     elif chg>0:
                         if abs(chg)>zzp:#pivot point
                             trend = 1 
                             print "pivot point",lastpx
                             df.loc[lastpx_idx,zzcol] = lastpx                            
                             print "see up trend",p0
                             lastpx = p0
                             lastpx_idx = index
        print "latest pivot point",lastpx
        df.loc[lastpx_idx,zzcol] = lastpx                            
        return df
    '''
    
    def calcPercent(self,data):
        zz_rets = (1+data.pct_change()).cumprod()
        zz_rets[0] = 1
        return zz_rets
          
    def drawChart(self,symbol,startDate):
        df = web.get_data_yahoo(symbol, startDate)
        px = df['Adj Close']
        px_rets = (1+px.pct_change()).cumprod()
        px_rets[0] = 1
        px_rets.plot()

        #print px
        self.chartkit.calcZigzag(df)
        #print df
        zzpx = df['zz'].dropna()
        zz_rets = self.calcPercent(zzpx)
        #zz_rets = (1+zzpx.pct_change()).cumprod()
        #zz_rets[0] = 1
        print type(zz_rets),zz_rets
        zz_rets.plot()
        plt.show()
        return
    def patternRec(self,data1,data2):
        return             
        
    def process(self):
        symbolLst = ['GOOG','^GSPC','VMW','IBM']
        sampleDict = {}
        for symbol in symbolLst:
            df = web.get_data_yahoo(symbol, '2015-01-01')
            df = self.chartkit.calcZigzag(df)
            zzpx = df['zz'].dropna()
            zz_rets = self.calcPercent(zzpx)
            sampleDict[symbol] = zz_rets
        for lhs in sampleDict:
            for rhs in sampleDict:
                if lhs!=rhs:
                    #print "compare",lhs,rhs
                    llen = len(sampleDict[lhs])
                    rlen = len(sampleDict[rhs])
                    minlen = min(llen,rlen)                        
                    cor,pval = pearsonr(sampleDict[lhs][:minlen],sampleDict[rhs][:minlen])
                    print lhs,"vs",rhs,"=",str(cor)
                    
    def process0(self):
        aapl = web.get_data_yahoo('GOOG', '2015-01-01')['Adj Close']
        msft = web.get_data_yahoo('IBM', '2015-01-01')['Adj Close']
        #print aapl
        #print msft
        aapl_rets = aapl.pct_change()
        msft_rets = msft.pct_change()
        aapl_rets[0] = 0
        msft_rets[0] = 0
        print aapl_rets
        print msft_rets
        corr = pd.rolling_corr(aapl_rets, msft_rets, 10)
        print type(corr),corr
        cor,pval = pearsonr(aapl_rets,msft_rets)
        print "pearsonr",str(cor),pval
        
        corr.plot()

    def process1(self):
        df1 = web.get_data_yahoo('GOOG', '2015-01-01')['Adj Close']
        df2 = web.get_data_yahoo('IBM', '2015-01-01')['Adj Close']
        s1_rets = self.calcPercent(df1)
        s2_rets = self.calcPercent(df2)
        s1_rets.plot()
        s2_rets.plot()
        plt.show()
        
    #find double top
    def process2(self):
        #goog
        #df1 = web.get_data_yahoo('GOOG', '2015-02-15','2015-03-31')
        df1 = web.get_data_yahoo('AAL', '2014-12-15','2015-05-8')
        ret = self.chartkit.doubletop(df1)
        print ret
        
        return
    def process3(self):
        #s1 = web.get_data_yahoo('AAL', '2014-12-15','2015-05-8')['Adj Close']
        s1 = web.get_data_yahoo('INTC', '2014-10-10','2015-01-21')['Adj Close']
        s2 = web.get_data_yahoo('AAL', '2015-06-09','2015-07-27')['Adj Close']
        n1 = np.array(s1.tolist())
        n2 = np.array(s2.tolist())
        
        print len(n1),len(n2)
        if (len(n2)<len(n1)):
            steps = (len(n2)*1.0-1.0)/(len(n1)-len(n2))
            x1 = np.arange(1,len(n2)+1)
            f = interp1d(x1, n2)
            print n2
            x_fake = np.arange(1.1, len(n2), steps)
            print len(x_fake)
            print x_fake
            c = np.sort(np.concatenate((x1, x_fake)))
            print c
            y1 = np.array([f(i) for i in c])
            print y1
                
        #s1=s1.reindex(index=np.arange(len(s1)))
        #print s1
        '''
        if (len(s2)<len(s1)):
            x2= pd.date_range(s1.index[0],s1.index[-1],freq='D')
            s2=s2.reindex(x2) 
        print s2
        '''
        a = pd.Series(n1)
        b = pd.Series(y1)
        rets1 = a.pct_change()
        rets2 = b.pct_change()
        
        rets1[0] = 0
        rets2[0] = 0
        
        print rets1
        print rets2 
        '''
        print type(rets1)
        corr = pd.rolling_corr(rets1, rets2, 10)
        print type(corr),corr
        cor,pval = pearsonr(rets1,rets2)
        print "pearsonr",str(cor),pval
        '''
        cor,pval = pearsonr(rets1,rets2)
        print "pearsonr",str(cor),pval
        print "def2",pearson_def(rets1,rets2)
        
        ##
        dist, cost, path = mlpy.dtw_std(rets1, rets2, dist_only=False)
        print "dist",dist
        pass        
if __name__ == "__main__":
    obj = StockChart()
    obj.process3()    
    #obj.drawChart('VMW','2015-01-01')