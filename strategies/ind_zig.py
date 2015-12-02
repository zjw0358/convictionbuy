from ind_base_px import BaseIndPx
from collections import OrderedDict
import math

class ind_zig(BaseIndPx):
    '''
    def usage(self):
        return "zig"

    #override func
    
    def setupParam(self,param):
        BaseIndPx.setupParam(self,param)  
        self.zzp = 3  
        if 'zzp' in param:
            self.zzp = int(param['zzp'])
    '''     
    def zig(self,df,zzp):
        #zzp = self.zzp
        trend = 0 #0-undefined,1-up,-1 down
        lastpx = 0
        lastpx_idx = 0
        zzcol = 'zz'

        for index, row in df.iterrows():
            #print index
            p0 = row['Adj Close']
            if lastpx==0:
                lastpx = p0
                lastpx_idx = index
                #print "first pivot",p0
                df.loc[index,zzcol] = p0
            else:
                chg = (p0/lastpx-1)*100
                #print p0,lastpx,round(chg,2)
                if trend==0:
                    if abs(chg)>zzp:
                        if chg>0:
                            trend = 1
                            #print "see up trend",p0
                        else:
                            trend = -1
                            #print "see down trend",p0
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
                            #print "pivot point",lastpx
                            df.loc[lastpx_idx,zzcol] = lastpx                            
                            #print "see down trend",p0
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
                             #print "pivot point",lastpx
                             df.loc[lastpx_idx,zzcol] = lastpx                            
                             #print "see up trend",p0
                             lastpx = p0
                             lastpx_idx = index
        #print "latest pivot point",lastpx
        df.loc[lastpx_idx,zzcol] = lastpx                         
        return df
        
    '''
    def trendline(self,df):
        pxfactor = 4.0
        #for index, row in df.iterrows():
        lastpx = df['Adj Close'].iloc[-1]
        print lastpx
        
        length = 0
        for idx in reversed(df.index):
            zzpx = df['zz'].loc[idx]
            if (not math.isnan(zzpx)):
                #print idx, df['zz'].loc[idx]
            
                aclose = df['Adj Close'].loc[idx]
                if ((zzpx/lastpx-1)*100 > pxfactor):
                    print idx,length,zzpx
                    break
            length+=1
            #px = df['zz'].loc[idx]
        pass
        
    def calcAngle0(self,df):
        pxfactor = 4.0        
        lastpx = df['Adj Close'].iloc[-1]
        print lastpx
        length = len(df)-1
        index = 0
        for row_index,row in df.iterrows():
            #aclose = row['Adj Close']
            #close = row['Close']
            zzpx = row['zz']
            if (not math.isnan(zzpx)):
                if (zzpx>lastpx):
                    r = (zzpx-lastpx)/(length-index)
                    print index,zzpx,lastpx,r
                    df.loc[row_index,'ang'] = r
                    df.loc[row_index,'offset'] = length-index
            index+=1
        top2 = df.sort_index(by='ang',ascending=False).head(2)
        #print top2
        return top2
        
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
        return (flag1 and flag2 and flag3)

    def findTrend(self, df):
        df0 = df.iloc[::-1]
        #print df0

        maxStartOffset = 10
        start = 0
        for row_index, row in df0.iterrows():
            if (start < maxStartOffset):
                lastpx = df0['Adj Close'].loc[row_index]
                #print lastpx
                toplst = self.calcAngle(df0,lastpx,start)
                flag = self.isDownTrend(toplst)
                if (flag):
                    print row_index,lastpx,"found downtrend"
                    return True;
            start+=1
        return False
        
    def calcAngle(self,df,lastpx,start):
        index = 0
        for row_index, row in df.iterrows():
            if (index>start):
                zzpx = row['zz']
                if (not math.isnan(zzpx)):
                    if (zzpx>lastpx):
                        r = (zzpx-lastpx)/(index - start)
                        #print index,zzpx,lastpx,r
                        df.loc[row_index,'ang'] = r
                        df.loc[row_index,'offset'] = index - start
            index+=1       
        top2 = df.sort_index(by='ang',ascending=False).head(2)
        return top2        
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)     
        df = self.algoFunc(ohlc)
        print self.findTrend(df)
#        self.trendline(df.dropna())
    '''
        
