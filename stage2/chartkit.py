import pandas as pd

class ChartKit:
    def __init__(self):
        return
        
    #df is pandas.dataframe
    def calcZigzag(self,df,zzp=3):
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
        
    def compare(self,df1,df2):
        df1 = self.calcZigzag(df1)
        df1 = df1['zz'].dropna()      
        x2= pd.date_range(df1.index[0],df1.index[-1],freq='D')
        df1=df1.reindex(x2)
        df1=df1.interpolate()
        
        df2 = self.calcZigzag(df2)
        df2 = df2['zz'].dropna()      
        x2= pd.date_range(df2.index[0],df2.index[-1],freq='D')
        df2=df2.reindex(x2)
        df2=df2.interpolate()
        
        

                
        pass  
    def doubletop(self,df):
        df1 = self.calcZigzag(df)
        df1 = df1['zz'].dropna()
        #print df1.index[0],df1.index[-1]
        
        x2= pd.date_range(df1.index[0],df1.index[-1],freq='D')
        df2=df1.reindex(x2)
        print df2.interpolate()
        #print df1.interpolate()
        #print df1
        '''
        pattern={}
        patime={}
        ptidx = 0
        pattern['e']=df1['zz'].iloc[-1]
        pattern['d']=df1['zz'].iloc[-2]
        pattern['c']=df1['zz'].iloc[-3]
        pattern['b']=df1['zz'].iloc[-4]
        pattern['a']=df1['zz'].iloc[-5]
        deltaa = abs(pattern['e']/pattern['c']-1)*100
        deltab = abs(pattern['b']/pattern['d']-1)*100
        if deltaa<1.5 and deltab<1.5:
            return True
        else:
            return False
        '''
        '''
        for idx in reversed(df1.index):
            if ptidx==0:
                pattern['e']=df1.loc[idx, 'zz']
                patime['e']=idx
                ptidx += 1
            else:
                
            print(idx, df1.loc[idx, 'zz'])
        '''     
        return