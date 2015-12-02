from ind_base_px import BaseIndPx
from collections import OrderedDict
import math
import ind_zig

class ind_trend(BaseIndPx):
    def __init__(self):
        self.zig = ind_zig.ind_zig()
        
    def usage(self):
        return "trend"

    #override func
    def setupParam(self,param):
        BaseIndPx.setupParam(self,param)  
        self.zzp = 3  
        if 'zzp' in param:
            self.zzp = int(param['zzp'])           
    
        
    def isDownTrend(self,df):
        if (len(df) < 2):
            return False
        gap = 1
        minoffset = 10
        r1v = df['ang'].iloc[0]
        r1o = df['offset'].iloc[0]
        r2v = df['ang'].iloc[1]
        r2o = df['offset'].iloc[1]
        flag1 = (abs(r1v-r2v)/r2v*100 < gap)
        flag2 = (r1o > minoffset)
        flag3 = (r2o-r1o) > r1o
        #print "\t",flag1,flag2,flag3,r1v,r2v,r1o,r2o
        print df
        return (flag1 and flag2 and flag3)

    def findTrend(self, df):
        df0 = df.iloc[::-1]
        #print df0

        maxStartOffset = 10
        start = 0
        for row_index, row in df0.iterrows():
            if (start < maxStartOffset):
                lastpx = df0['Adj Close'].loc[row_index]
                #print "test",start,row_index,lastpx
                df0['ang']=float('nan')
                toplst = self.calcAngle(df0,lastpx,start)
                flag = self.isDownTrend(toplst)
                if (flag):
                    print row_index,lastpx,"found downtrend breakout"
                    return True;
                # drop ang
                #df0.drop('ang', axis=1, inplace=True)

            start+=1
        return False
        
    def calcAngle(self,df,lastpx,start):
        index = 0
        for row_index, row in df.iterrows():
            if (index>start):
                #print index,row_index
                zzpx = row['zz']
                if (not math.isnan(zzpx)):
                    if (zzpx>lastpx):
                        r = (zzpx-lastpx)/(index - start)
                        #print index,zzpx,lastpx,r
                        df.loc[row_index,'ang'] = r
                        df.loc[row_index,'offset'] = index - start
            index+=1
        #print df     
        top2 = df.sort_index(by='ang',ascending=False).head(2)
        return top2.dropna()
              
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)     
        df = self.zig.zig(ohlc,self.zzp)
        self.ind['breakout'] = self.findTrend(df)
#        self.trendline(df.dropna())
        
