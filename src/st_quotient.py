# -*- coding: utf-8 -*-
import math
import pandas
from collections import defaultdict
import operator
#import tradesupport
#import simutable
#import numpy


class st_quotient:
    def __init__(self,bt):
        self.stname = "quotient" #strategy name
        #setup component
        self.support = bt.getTradeSupport()
        self.simutable = bt.getSimuTable()

    def setup(self,k1,k2,cl):
        self.k1=k1
        self.k2=k2
        self.cutoffLength = cl  
        self.alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
        self.a1 = math.exp(-1.414 * math.pi / self.cutoffLength);
        self.b1 = 2 * self.a1 * math.cos(math.radians(1.414 * 180 / self.cutoffLength));
        self.c2 = self.b1
        self.c3 = - self.a1**2
        self.c1 = 1 - self.c2 - self.c3;

        self.hplst=[]
        self.filtlst=[]
        self.nrflst=[]
        self.quolst=[]
        self.shortquolst=[]
        self.peaklst=[]
        self.pricelst=[]

        print "=== ST_QUOTIENT ==============================================="
        print "k1",self.k1
        print "k2",self.k2
        print "cutoff length",self.cutoffLength
        print "alpha1,",self.alpha1
        print "(1 - alpha1 / 2)*(1 - alpha1 / 2),",(1 - self.alpha1 / 2)*(1 - self.alpha1 / 2) 
        print "a1,",self.a1
        print "b1,",self.b1
        print "c1,",self.c1
        print "c2,",self.c2
        print "c3,",self.c3  
        print "================================================================"

    def getStrategyName(self):
        return self.stname

    def process(self,bt,symbol,param,ohlc_px,spy_px):
        # parameter
        k1 = 0.7
        k2 = 0.4
        cl = 25
        if 'k1' in param:
            k1 = float(param['k1'])
        if 'k2' in param:
            k2 = float(param['k2'])
        if 'cl' in param:
            cl = int(param['cl'])
        
        
        #different approach
        
        if param['mode']=='1':
            self.processOptimization(symbol,ohlc_px,spy_px)
            return None
        elif param['mode']==None or param['mode']=='0':            
            self.setup(k1,k2,cl)
            dv = self.processAllPriceData(ohlc_px)
            return dv
        return None

    # process single data        
    def procSingleData(self,index,price):
        self.hplst.append(0.)
        self.filtlst.append(0.)
        self.peaklst.append(0.)
        self.quolst.append(0.)
        self.shortquolst.append(0.)
        self.nrflst.append(0.)
        self.pricelst.append(price)
        price1=0.
        price2=0.
        hp1=0.
        hp2=0.
        filt1=0.
        filt2=0.
        peak1=0.
        
        if index >=1:
            price1= self.pricelst[index-1]
            hp1 = self.hplst[index-1]
            filt1 = self.filtlst[index-1]
            peak1 = self.peaklst[index-1]
            if index >= 2:
                price2= self.pricelst[index-2]
                hp2 = self.hplst[index-2]
                filt2 = self.filtlst[index-2]                
    
        hp0 = (1 - self.alpha1 / 2)*(1 - self.alpha1 / 2) * (price - 2 * price1 + price2) + 2 * (1 - self.alpha1) * hp1 - (1 - self.alpha1)*(1 - self.alpha1) * hp2;
        self.hplst[index]=hp0
                
        filt = self.EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2);
        self.filtlst[index]=filt
        
        #fast attack            
        peak0 = peak1*0.991
        
        af = abs(filt)
        if af > peak0:
            peak0 = af
        self.peaklst[index] = peak0
        
        NormRoofingFilter = filt / peak0;
        Quotient1 = (NormRoofingFilter + self.k1) / (self.k1 * NormRoofingFilter + 1);
        Quotient2 = (NormRoofingFilter + self.k2) / (self.k2 * NormRoofingFilter + 1);
        
        self.quolst[index]=Quotient1
        self.shortquolst[index]=Quotient2
        
        self.nrflst[index]=NormRoofingFilter
        
        #must be placed before trigger signal(to avoid buying ahead)
        #self.support.processData(index)            

        prevQuotient = self.quolst[index-1]
        prevShortQuo = self.shortquolst[index-1]
        
        if prevQuotient<0 and Quotient1>=0:
            self.support.buyorder(self.stname)
                
        if prevShortQuo>0 and Quotient2<=0:
            self.support.sellorder(self.stname)
        
        # day to day value
        #self.support.setDailyValue(index)

        
    def processAllPriceData(self,ohlc):
        self.support.setup(ohlc,10000)
        return self.quotient(ohlc)

    def processOptimization(self,symbol,ohlc,bm):
        length = range(10, 55, 5)
        k1set = [x * 0.1 for x in range(6, 10)]
        k2set = [x * 0.1 for x in range(1, 5)]
        #dd = defaultdict(dict)
        #writer = pandas.ExcelWriter('output.xlsx')        
        
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        #pandas.set_option('display.expand_max_repr', False)
        #columns = ['param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order'] #,

        #must setup report tool before simulation test
        self.simutable.setupSymbol(symbol,bm)

        #dftbl = pandas.DataFrame(columns=columns,index=length) 
        #dftbl = pandas.DataFrame(columns=columns) 

        for k2 in k2set:
            for k1 in k1set: 
                for cl in length:
                    self.setup(k1,k2,cl)
                    self.support.setup(ohlc,10000)
                    df = self.quotient(ohlc)
                    
                    param = "k1=%.1f,k2=%.1f,cf=%d"%(k1,k2,cl)
                    self.simutable.addSymbolResult(param,df)
        
        #add results to report
        self.simutable.makeSymbolReport()
        
       
        #print "max=",max(dd.iteritems(), key=operator.itemgetter(1))[0]
        return

    #def setup(self,deposit):
    #    self.deposit = deposit
    #    self.shares = 0
        
    
        
  
                
    def drawChart(self,ax,sdatelabel):
        ax.set_ylim([-1,1])
        ax.set_yticks([-0.5,0.5])
        ax.plot(sdatelabel[self.offset:], self.df['quo1'][self.offset:])
        ax.plot(sdatelabel[self.offset:], self.df['quo2'][self.offset:])
        ax.axhline(0, color='r')
     
    def config(self,name,value):
        print "quostgy",name,value  

    #def getOffset(self):
    #    return self.offset
    
    ##################
    # implementation #
    ##################
    
    
    #def getMeanpx(self,ohlc_px,index):
    #    return (ohlc_px['Open'][index]+ohlc_px['Close'][index]+ohlc_px['High'][index]+ohlc_px['Low'][index])/4

    def EhlersSuperSmootherFilter(self,hp0,hp1,filt1,filt2):
        filt =  self.c1 * (hp0 + hp1) / 2 + self.c2 * filt1 + self.c3 * filt2;
        return filt


    def quotient(self,ohlc_px):    
        hplst=[]
        filtlst=[]
        nrflst=[]
        quolst=[]
        shortquolst=[]
        peaklst=[]
        pricelst = ohlc_px['Adj Close']        
        
        for index in range(0, len(pricelst)):
            hplst.append(0.)
            filtlst.append(0.)
            peaklst.append(0.)
            quolst.append(0.)
            shortquolst.append(0.)
            nrflst.append(0.)
            
            price = pricelst[index]
            
            price1=0.
            price2=0.
            hp1=0.
            hp2=0.
            filt1=0.
            filt2=0.
            peak1=0.
            if index >=1:
                price1= pricelst[index-1]
                hp1 = hplst[index-1]
                filt1 = filtlst[index-1]
                peak1 = peaklst[index-1]
                if index >= 2:
                    price2= pricelst[index-2]
                    hp2 = hplst[index-2]
                    filt2 = filtlst[index-2]                
        
            hp0 = (1 - self.alpha1 / 2)*(1 - self.alpha1 / 2) * (price - 2 * price1 + price2) + 2 * (1 - self.alpha1) * hp1 - (1 - self.alpha1)*(1 - self.alpha1) * hp2;
            hplst[index]=hp0            
                    
            filt = self.EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2);
            filtlst[index]=filt
            
            #fast attack            
            peak0 = peak1*0.991
            
            af = abs(filt)
            #print type(af),type(filt),type(peak0)
            if af > peak0:
                peak0 = af
            #print index,peak0,peak1
            #peak1 = peak0
            peaklst[index] = peak0
            
            NormRoofingFilter = filt / peak0;
            Quotient1 = (NormRoofingFilter + self.k1) / (self.k1 * NormRoofingFilter + 1);
            Quotient2 = (NormRoofingFilter + self.k2) / (self.k2 * NormRoofingFilter + 1);
            
            quolst[index]=Quotient1
            shortquolst[index]=Quotient2
            
            nrflst[index]=NormRoofingFilter
            
            #must be placed before trigger signal(to avoid buying ahead)
            self.support.processData(index)            

            prevQuotient = quolst[index-1]
            prevShortQuo = shortquolst[index-1]
            
            if prevQuotient<0 and Quotient1>=0:
                self.support.buyorder()
                    
            if prevShortQuo>0 and Quotient2<=0:
                self.support.sellorder()
            
            # day to day value
            self.support.setDailyValue(index)
            
            #print index,pricelst[index],hplst[index],filtlst[index],peaklst[index],nrflst[index],quolst[index]         
            #print "return quolst=",len(quolst)
            #print "buyorder=",buyorder
            #print "sellorder=",sellorder
            #backtest(buyorder,sellorder,pricelst,datelst)
            
        #self.report = pandas.DataFrame({'order':self.ser_orders,'price':self.ser_price,'pnl':self.ser_pnl},index=self.ser_orderdate)
        #print self.report
        #print self.report['pnl'].sum()
        #self.df = pandas.DataFrame({'quo1':quolst,'quo2':shortquolst,'dayvalue':dailyvalue},index=ohlc_px.index.values)
        #self.report = self.support.getTradeReport()
        return self.support.getDailyValue()

