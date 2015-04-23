import pandas.io.data as web
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats.stats import pearsonr 

class StockChart:
    def __init__(self):
        return

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
        self.calcZigzag(df)
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
            df = self.calcZigzag(df)
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

                
if __name__ == "__main__":
    obj = StockChart()
    obj.process1()    
    #obj.drawChart('VMW','2015-01-01')