#import math
import pandas as pd
import datetime
import numpy

'''
strategy description
price0=sold price
price1=mean(close price of N days after earning day)
if price1<price0, no 'buy' signal
if price1>price0, give 'buy' signal
'''

class st_erdate:
    def __init__(self,bt):
        self.cleanup()
        self.stname = "erdate" #strategy name
        #setup component
        self.tradesup = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()
        self.path = bt.getDataPath()
        
    def cleanup(self):
        self.erlst=[]
        self.erdidx=0
        self.obvwin=1
        self.toHandlePostErd=False
        return
        
    def setup(self,win):
        self.obvwin=win
        print "========ST_ERDATE SETUP ========================================"
        print "+ observed windows1=",self.obvwin
        print "================================================================"

    def getStrategyName(self):
        return self.stname
    
    def procSingleData(self,index,price):
        if self.erdf['er'].iloc[index]=='s':
            self.tradesup.sellorder(self.stname)
            self.erdidx=index+1
            self.toHandlePostErd=True
        elif self.toHandlePostErd==True and index>self.erdidx:            
            if (index-self.erdidx)>=self.obvwin:                
                self.tradesup.buyorder(self.stname)
                self.toHandlePostErd = False
            elif price>self.tradesup.getLastSellPrice():
                self.tradesup.buyorder(self.stname)
                self.toHandlePostErd = False
        else:
            self.tradesup.buyorder(self.stname)
        return
        
        
    def runStrategy(self,symbol,ohlc_px):
        self.tradesup.setup(ohlc_px,10000)
        self.loadERDfile(symbol)
        if len(self.erlst)==0:
            return None
        self.erdf =  pd.DataFrame(index=ohlc_px.index,columns=['er']) 
       
        for d in self.erlst:
            if d in self.erdf.index:
                self.erdf.loc[d,'er']='s' # sell signal
        self.erdf['er']=self.erdf['er'].shift(-1)

      

    def process(self,bt,symbol,param,ohlc_px,spy_px):
        #for row in ohlc_px.iterrows():
        #    print row
        #print self.erdf
        return None

########################################################################
#  optional functions
########################################################################
    def loadERDfile(self,symbol):        
        fileName=self.path+symbol+"_erdate.erd"
        fp = open(fileName,'r',-1)

        for line in fp:
            #print line
            d = datetime.datetime.strptime(line, '%m/%d/%Y\n') #convert datetime
            self.erlst.append(d)
        fp.close()
        