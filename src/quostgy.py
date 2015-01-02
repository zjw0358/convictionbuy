# -*- coding: utf-8 -*-
import basestrategy
import math
import pandas
from collections import defaultdict
import operator
import support
#import numpy


class quostgy(basestrategy.basestrategy):
    def __init__(self): 
        self.deposit = 10000
        self.shares = 0
        self.offset = 0   
        self.cutoffLength = 20;
        self.k1 = 0.9;
        self.k2 = 0.4
        self.alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
        self.a1 = math.exp(-1.414 * math.pi / self.cutoffLength);
        self.b1 = 2 * self.a1 * math.cos(math.radians(1.414 * 180 / self.cutoffLength));
        self.c2 = self.b1
        self.c3 = - self.a1**2
        self.c1 = 1 - self.c2 - self.c3;
        print "alpha1,",self.alpha1
        print "(1 - alpha1 / 2)*(1 - alpha1 / 2),",(1 - self.alpha1 / 2)*(1 - self.alpha1 / 2) 
        print "a1,",self.a1
        print "b1,",self.b1
        print "c1,",self.c1
        print "c2,",self.c2
        print "c3,",self.c3

        
    def procSingleData(self,price):
        return
        
    def procMultiData(self,df):
        return self.quotient(df)

    def processOptimization(self,ohlc,bm):
        length = range(10, 30, 5)
        dd = defaultdict(dict)
        
        columns = ['alpha', 'beta','perf']
        dftbl = pandas.DataFrame(columns=columns,index=length) 

        for cl in length:
            self.init(0.9,0.4,cl)
            df = self.quotient(ohlc)
            offset = self.getOffset()
            rtbm = bm[offset:].resample('M',how='last')
            bm_returns = rtbm.pct_change()        
            bm_returns=bm_returns.dropna()
            rtsgy = df['dayvalue'][offset:].resample('M',how='last')
            sgy_returns = rtsgy.pct_change()
            sgy_returns=sgy_returns.dropna()
            dct = support.basefacts(bm_returns,sgy_returns)
            perfdata = self.getPerf()

            #d0 = {'alpha':dct['alpha'],'beta':dct['beta'],'perf':perfdata}
            #d0 = {dct['alpha'],dct['beta'],perfdata}
            dftbl.loc[cl,'alpha'] = dct['alpha']
            dftbl.loc[cl,'beta'] = dct['beta']
            dftbl.loc[cl,'perf'] = perfdata
            #d1 = pandas.DataFrame(d0,index=[cl])
            #dftbl.append(d1)
            #dftbl.loc[len(dftbl)+1]=d0
            
            #dd[cl] = self.getPerf()
            #print cl," performance=",dd[cl]

            
        
        print dftbl
        #print "max=",max(dd.iteritems(), key=operator.itemgetter(1))[0]
        return
    def setup(self,deposit):
        self.deposit = deposit
        self.shares = 0
        
    #for optimization test        
    def init(self,k1,k2,cf):
        self.k1=k1
        self.k2=k2
        self.cutoffLength = cf
        self.deposit = 10000
        self.shares = 0
        self.offset = 0   
        self.alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
        self.a1 = math.exp(-1.414 * math.pi / self.cutoffLength);
        self.b1 = 2 * self.a1 * math.cos(math.radians(1.414 * 180 / self.cutoffLength));
        self.c2 = self.b1
        self.c3 = - self.a1**2
        self.c1 = 1 - self.c2 - self.c3;
        
  
                
    def drawChart(self,ax,sdatelabel):
        ax.set_ylim([-1,1])
        ax.set_yticks([-0.5,0.5])
        ax.plot(sdatelabel[self.offset:], self.df['quo1'][self.offset:])
        ax.plot(sdatelabel[self.offset:], self.df['quo2'][self.offset:])
        ax.axhline(0, color='r')
     
    def config(self,name,value):
        print "quostgy",name,value  

    def getOffset(self):
        return self.offset
    
    ##################
    # implementation #
    ##################
    
    
    def getMeanpx(self,ohlc_px,index):
        return (ohlc_px['Open'][index]+ohlc_px['Close'][index]+ohlc_px['High'][index]+ohlc_px['Low'][index])/4

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
        buyorder=[]
        sellorder=[]
        buyFlag = False
        order=0 #0 nothing,1-buy,2-sell
        dailyvalue=[]
        pricelst = ohlc_px['Adj Close']
        
        self.ser_orders = []
        self.ser_orderdate = []
        self.ser_pnl = []
        self.ser_price = []
        self.ser_dayvalue = []
        self.total_order = 0
        self.profit_order = 0
        self.loss_order = 0
        self.trancost = 0
        
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
                
            
                #alpha1 = (math.cosh(math.sqrt(2) * math.pi / 100) + math.sinh (math.sqrt(2) * math.pi / 100) - 1) / math.cosh(math.sqrt(2) * math.pi / 100)
                #alpha1 = (math.cos(0.707*math.pi*2 / 100) + math.sin (0.707*math.pi*2 / 100) - 1) / math.cos(0.707*math.pi*2 / 100)
        
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
            
            
            
            if order==1:
                order=0
                buyorder.append(index)
                buyFlag = True

#find a mean price   
                #print index         
                #print ohlc_px['Open'][index]
                '''print ohlc_px.loc[index,'Close']
                print ohlc_px.loc[index,'High']
                print ohlc_px.loc[index,'Low']'''

                meanpx = self.getMeanpx(ohlc_px,index)
                buypower = support.getBuyPower(self.deposit)
                self.shares = int(buypower/meanpx)
                #self.shares = self.deposit/meanpx 
                self.trancost = self.shares*meanpx + support.buycomm(self.shares*meanpx)
                self.deposit = self.deposit-self.trancost
                if self.offset==0:
                    self.offset = index
                datelb = ohlc_px.index[index].to_pydatetime()

                self.ser_orders.append('buy')
                self.ser_orderdate.append(ohlc_px.index[index])
                self.ser_pnl.append(None)
                self.ser_price.append(meanpx)
                print datelb," buy ",self.shares,"@",meanpx,",commission=",support.buycomm(self.shares*meanpx),",remain=",self.deposit#,",ohlc=",ohlc_px['Open'][index],ohlc_px['Close'][index],ohlc_px['High'][index],ohlc_px['Low'][index]
            elif order==2:
                order=0
                meanpx = self.getMeanpx(ohlc_px,index)
                sellcomm = support.sellcomm(self.shares*meanpx)
                trancost = self.shares*meanpx-sellcomm
                self.deposit = self.deposit+trancost  #pricelst[index]
                shares = self.shares
                self.shares = 0
                sellorder.append(index)
                buyFlag = False
                datelb = ohlc_px.index[index].to_pydatetime()
                
                self.ser_orders.append('sell')
                self.ser_orderdate.append(ohlc_px.index[index])
                pnl = trancost - self.trancost
                self.ser_pnl.append(pnl)
                self.ser_price.append(meanpx)
                if pnl>=0:
                    self.profit_order+=1
                else:
                    self.loss_order+=1
                
                print datelb," sell ",shares,"@",meanpx,",commission=",sellcomm,",remain=",self.deposit#,",ohlc=",ohlc_px['Open'][index],ohlc_px['Close'][index],ohlc_px['High'][index],ohlc_px['Low'][index]
            #buy order 
            prevQuotient = quolst[index-1]
            prevShortQuo = shortquolst[index-1]
            if prevQuotient<0 and Quotient1>=0 and buyFlag==False:                
                order=1
                '''buyorder.append(index)
                buyFlag = True
                self.shares = self.deposit/pricelst[index]
                self.deposit = 0
                if self.offset==0:
                    self.offset = index'''
                
            
                    
            if prevShortQuo>0 and Quotient2<=0 and buyFlag==True:                
                order=2
                '''self.deposit = self.shares*pricelst[index]
                self.shares = 0
                sellorder.append(index)
                buyFlag = False'''
            
            # day to day value
            dailyvalue.append(self.deposit+self.shares*pricelst[index])
            
            #print index,pricelst[index],hplst[index],filtlst[index],peaklst[index],nrflst[index],quolst[index]         
        #print "return quolst=",len(quolst)
        #print "buyorder=",buyorder
        #print "sellorder=",sellorder
        #backtest(buyorder,sellorder,pricelst,datelst)
        self.report = pandas.DataFrame({'order':self.ser_orders,'price':self.ser_price,'pnl':self.ser_pnl},index=self.ser_orderdate)
        print self.report
#        print self.report['pnl'].sum()
        self.df = pandas.DataFrame({'quo1':quolst,'quo2':shortquolst,'dayvalue':dailyvalue},index=ohlc_px.index.values)
        return self.df

    def getPerf(self):
        return self.report['pnl'].sum()