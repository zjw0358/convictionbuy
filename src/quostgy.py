# -*- coding: utf-8 -*-
import basestrategy
import math
import pandas
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

    def setup(self,deposit):
        self.deposit = deposit
        self.shares = 0

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
    # implementation
    #
    #
    #
    #
    
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
#        open_px = ohlc_px['Open']
#        print open_px
        
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
                #(ohlc_px['Open'][index]+ohlc_px['Close'][index]+ohlc_px['High'][index]+ohlc_px['Low'][index])/4
                self.shares = self.deposit/meanpx #pricelst[index]
                self.deposit = 0
                if self.offset==0:
                    self.offset = index
                datelb = ohlc_px.index[index].to_pydatetime()
                print datelb," buy @",meanpx,",ohlc=",ohlc_px['Open'][index],ohlc_px['Close'][index],ohlc_px['High'][index],ohlc_px['Low'][index]
            elif order==2:
                order=0
                meanpx = self.getMeanpx(ohlc_px,index)
                self.deposit = self.shares*meanpx  #pricelst[index]
                self.shares = 0
                sellorder.append(index)
                buyFlag = False
                print datelb," sell @",meanpx,",ohlc=",ohlc_px['Open'][index],ohlc_px['Close'][index],ohlc_px['High'][index],ohlc_px['Low'][index]
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
        
        self.df = pandas.DataFrame({'quo1':quolst,'quo2':shortquolst,'dayvalue':dailyvalue},index=ohlc_px.index)
        return self.df

