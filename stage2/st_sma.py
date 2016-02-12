'''
simple moving average strategy
'''

from ind_ma import ind_ma
from st_pattern import StrategyPattern
from trade_support import TradeSupport

def foo(row):
    
    pass
    
class st_sma(ind_ma):
    def usage(self):
        return "nbar=3"
   
    def runIndicator(self,symbol,ohlc,param={}):
        if 'nbar' in param:
            self.nbar = int(param['nbar'])
        else:
            self.nbar = 2
            
        ind_ma.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy(ohlc)
        pass
    
    def algoStrategy(self, ohlc):
        # price cross above MA10 and crosee below MA10
        sp = StrategyPattern()
        tsup = TradeSupport()
        px = ohlc['Adj Close']
        if (self.ma10):
            # not using divergencyCross 
            buysg,sellsg = sp.cross(px, self.ma10, self.nbar)
            tsup.getLastSignal(buysg,sellsg,self.ind,'ma10b','ma10s')
            '''
            ohlc['ma10b']=buysg
            ohlc['ma10s']=sellsg
            ohlc['ma10']=self.ma10
            '''
        if (self.ma50):
            buysg,sellsg = sp.cross(px, self.ma50, self.nbar)
            tsup.getLastSignal(buysg,sellsg, self.ind,'ma50b','ma50s')            

        if (self.ma50 and self.ma10):
            buysg,sellsg = sp.cross(self.ma10, self.ma50, self.nbar)
            tsup.getLastSignal(buysg,sellsg, self.ind,'ma1050b','ma1050s')            
            # ready to cross above
            flag1 = (self.ma10[-1] > self.ma50[-1]*0.97)
            dif1 =  (self.ma50[-1]-self.ma10[-1])
            dif2 = (self.ma50[-2]-self.ma10[-2])
            dif3 = (self.ma50[-3]-self.ma10[-3])
            flag2 = (dif1<dif2) and (dif2<dif3) and (dif1>0)
            if (flag1 and flag2):
                self.ind['ma1050e']=1
            else:
                self.ind['ma1050e']=0
            
        #too lag, how about px cross MA50
        '''
        l1=len(self.ma50)
        l2=len(self.ma200)
        if (l1!=l2):
            print l1,l2
            print self.ma200
            print "========"
            print self.ma50  
        '''
        l1=len(self.ma50)
        l2=len(self.ma200)
        if (l1==l2 and l1>0):
            #print "test golder and death"
            buysg,sellsg = sp.cross(self.ma50, self.ma200, self.nbar)
            #print sellsg
            tsup.getLastSignal(buysg,sellsg, self.ind,'ma50200b','ma50200s')          
        
        #support line
        #l1=len(px)
        #l2=len(self.ma50)
        #print l1,l2
        #print ohlc
        
        buysg,sellsg = sp.supportline(px, self.ma50, self.nbar)
        tsup.getLastSignal(buysg,sellsg, self.ind,'sup50','res50')          
        #print ohlc
        pass

    # column is too long
    def merge(self,df):
        coldict = {"ma10b":"ma10s","ma50b":"ma50s",'ma1050b':'ma1050s','ma50200b':'ma50200s'}
        lst=[]
        for index, row in df.iterrows():
            for key in coldict:
                c1 = key
                c2 = coldict[key]
                lst.append(c1)
                lst.append(c2)
                colm = c1+'s'
                if (row[c1] < row[c2]):
                    df.loc[index,colm] = row[c1]
                else:
                    df.loc[index,colm] = -row[c2]
        df.drop(lst, axis=1, inplace=True)        
        return df
        
    def runScan(self, df):
        col = df.columns.values 
        if not self.param:
            return df,col
        if 'merge' in self.param:
            df = self.merge(df)
            default_col = ['ma10','ma50','ma200','ma10bs','ma50bs','ma1050bs','ma50200bs']
            col = df.columns.values 
            #return df,col
            return df,default_col
        else:
            return ind_ma.runScan(self,df)
