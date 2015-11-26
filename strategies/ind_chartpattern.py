from ind_base_px import BaseIndPx

 #df is pandas.dataframe
def calcZigzag(df,zzp=3):
    trend = 0 #0-undefined,1-up,-1 down
    lastpx = 0
    lastpx_idx = 0
    zzcol = 'zz'
    for index, row in df.iterrows():
        #print index
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
        
class ind_chartpattern(BaseIndPx):
    def runIndicator(self,symbol,ohlc,param={}):
        #print ohlc
        self.setupParam(param)     
        #self.close_px = ohlc['Adj Close']
        #algoFunc(ohlc)   
        