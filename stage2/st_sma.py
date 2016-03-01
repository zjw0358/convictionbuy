'''
simple moving average strategy
'''

from ind_ma import ind_ma
from st_pattern import StrategyPattern
from trade_support import TradeSupport
import pandas


class st_sma(ind_ma):
    def usage(self):
        return "nbar=3"
   
    def runIndicator(self,symbol,ohlc,param={}):
        if 'nbar' in param:
            self.nbar = int(param['nbar'])
        else:
            self.nbar = 2
            
        if 'volra' in param:
            self.volra = float(param['volra'])
        else:
            self.volra = 1.4

        if 'dist50' in param:
            self.dist50 = float(param['dist50'])
        else:
            self.dist50 = 20

        ind_ma.runIndicator(self,symbol,ohlc,param)
        #print "process st_sma",symbol
        self.algoStrategy(symbol, ohlc)
        pass
    
    def algoStrategy(self, symbol, ohlc):
        # price cross above MA10 and crosee below MA10
        sp = StrategyPattern()
        tsup = TradeSupport()
        px = ohlc['Adj Close']
        if (not self.ma10.empty):
            # not using divergencyCross
            buysg,sellsg = sp.cross(px, self.ma10, self.nbar)
            tsup.getLastSignal(buysg,sellsg,self.ind,'ma10b','ma10s')
            ohlc['ma10b']=buysg
            ohlc['ma10s']=sellsg
            #ohlc['ma10']=self.ma10

        ma50bsg = []
        if not self.ma50.empty:
            buysg,sellsg = sp.cross(px, self.ma50, self.nbar)
            tsup.getLastSignal(buysg, sellsg, self.ind, 'ma50b', 'ma50s')
            ohlc['ma50b'] = buysg
            ohlc['ma50s'] = sellsg
            ma50bsg = buysg

            s1 = pandas.rolling_mean(self.ma50, 3) #.tolist()
            s2 = s1.shift(2)
            delta = s1 - s2
            buysg, sellsg = sp.crossValue(delta, delta, 0, 0, 1)
            tsup.getLastSignal(buysg, sellsg, self.ind, 'ag50b', 'ag50s')
            ohlc['ag50b'] = buysg
            ohlc['ag50s'] = sellsg

            # TODO
            # #buysg,sellsg = sp.supportline(px, self.ma50, self.nbar)
            #tsup.getLastSignal(buysg, sellsg, self.ind, 'sup50', 'res50')


        if (not self.ma50.empty) and (not self.ma10.empty):
            buysg, sellsg = sp.cross(self.ma10, self.ma50, self.nbar)
            tsup.getLastSignal(buysg, sellsg, self.ind, 'ma1050b', 'ma1050s')
            ohlc['ma1050b'] = buysg
            ohlc['ma1050s'] = sellsg

            # find the distance
            #self.dist50 = 20
            lastsell = -self.dist50
            distsg = []
            for idx, val in enumerate(ohlc['ma50s']):
                sig = ""
                if val == "sell":
                    lastsell = idx
                    #print "dist50",idx
                buyval = ma50bsg[idx]
                if (buyval == "buy"):
                    #TODO test
                    if symbol=="QCOM":
                        print "dist50",idx,lastsell,self.dist50
                    if lastsell >= 0 and idx-lastsell > self.dist50:
                        sig = "buy"
                    else:
                        sig = ""
                distsg.append(sig)
            ohlc['dist50'] = distsg
            tsup.getLastSignal(distsg, [], self.ind, 'dist50', '')
            #print self.ind

            # ready to cross above
            '''
            flag1 = (self.ma10[-1] > self.ma50[-1]*0.97)
            dif1 = (self.ma50[-1]-self.ma10[-1])
            dif2 = (self.ma50[-2]-self.ma10[-2])
            dif3 = (self.ma50[-3]-self.ma10[-3])
            flag2 = (dif1<dif2) and (dif2<dif3) and (dif1>0)
            if (flag1 and flag2):
                self.ind['ma1050e']=1
            else:
                self.ind['ma1050e']=0
            '''
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
        #print self.ma50


        
        #volume
        buysg,sellsg = sp.cross2factors(px, self.volma20ra, self.ma10, self.volra, 2)
        tsup.getLastSignal(buysg, sellsg, self.ind, 'vol10b', 'vol10s')
        ohlc['vol10b'] = buysg
        ohlc['vol10s'] = sellsg

        #debug
        #ohlc['ma50']=self.ma50        
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
            return df, col
        if 'merge' in self.param:
            df = self.merge(df)
            default_col = ['ma10','ma50','ma200','ma10bs','ma50bs','ma1050bs','ma50200bs']
            col = df.columns.values 
            #return df,col
            return df,default_col
        else:
            return ind_ma.runScan(self,df)
