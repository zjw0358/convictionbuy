from collections import OrderedDict
import numpy as np
import pandas

class st_reuterfa:
    def __init__(self):
        self.cleanup()
        self.stname = "st_reuterfa" #strategy name
    
    def cleanup(self):
        self.ind = OrderedDict()
        self.pxdf = pandas.DataFrame(columns=['symbol','q5','q4','q3','q2','q1','q0'])
        self.sgyparam={}
        return

    def usage(self):
        return ""

        
    def setupParam(self,param):
        '''
        if 'eps' in param:
            self.sgy="eps"            
        '''
        self.sgyparam = param
        return
        
    # it is price data module(need real price data)
    def needPriceData(self):
        return True

    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)
     
        close_px = ohlc['Adj Close']
        self.algoFunc(symbol, close_px)  
              
    def getIndicators(self):
        return self.ind  
   
    def algoFunc(self, symbol, px):
        if 'px' in self.sgyparam:
            px = px.resample('Q',how='last',fill_method='bfill')  #backward filling
            pxlst = px.values.tolist()
            pxlen = len(pxlst)
            print px
    
            newrow = len(self.pxdf)+1        
            self.pxdf.loc[newrow,'symbol']= ("%s_px"%symbol)
            if pxlen>9:
                self.pxdf.loc[newrow,'q5']= pxlst[-6]/pxlst[-10]-1
            if pxlen>8:
                self.pxdf.loc[newrow,'q4']= pxlst[-5]/pxlst[-9]-1
            if pxlen>7:
                self.pxdf.loc[newrow,'q3']= pxlst[-4]/pxlst[-8]-1
            if pxlen>6:
                self.pxdf.loc[newrow,'q2']= pxlst[-3]/pxlst[-7]-1      
            if pxlen>5:
                self.pxdf.loc[newrow,'q1']= pxlst[-2]/pxlst[-6]-1        
            if pxlen>4:
                self.pxdf.loc[newrow,'q0']= pxlst[-1]/pxlst[-5]-1
        #print df
        #print lst
        
    #post process        
    def runScan(self,df): 
        if 'eps' in self.sgyparam:
            df['q5'] = df['epsqtr-5']/df['epsqtr-9']-1
            df['q4'] = df['epsqtr-4']/df['epsqtr-8']-1
            df['q3'] = df['epsqtr-3']/df['epsqtr-7']-1
            df['q2'] = df['epsqtr-2']/df['epsqtr-6']-1
            df['q1'] = df['epsqtr-1']/df['epsqtr-5']-1              
            df['q0'] = df['epsqtr0']/df['epsqtr-4']-1
            #newrow = len(self.pxdf)+1
            for index, row in df.iterrows():
                df.loc[index,'symbol'] = ("%s_eps"%row['symbol'])
        if len(self.sgyparam)>0:        
            df=df[['symbol','q5','q4','q3','q2','q1','q0']]
            df = df.append(self.pxdf) 
        print df
        return df
