'''
quotient, 2014 Aug stock technical analysis magzine
'''
import math
import pandas
from ind_base_px import BaseIndPx

class ind_quotient(BaseIndPx):
    def usage(self):
        return "k1=len1&k2=len2&cl=len3"

    ############################################################################
    # ALGORITHM
    ############################################################################            
    def EhlersSuperSmootherFilter(self,hp0,hp1,filt1,filt2):
        filt =  self.c1 * (hp0 + hp1) / 2 + self.c2 * filt1 + self.c3 * filt2;
        return filt
    
    # do remember to call parent's setupParam()    
    def setupParam(self,param):
        #print "in ind_quotient setupParam",param
        BaseIndPx.setupParam(self,param)
        # default parameter
        self.k1 = 0.8
        self.k2 = 0.4
        self.cl = 25
        if 'k1' in param:
            self.k1 = float(param['k1'])
        if 'k2' in param:
            self.k2 = float(param['k2'])
        if 'cl' in param:
            self.cl = int(param['cl'])
            
        self.alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
        self.a1 = math.exp(-1.414 * math.pi / self.cl);
        self.b1 = 2 * self.a1 * math.cos(math.radians(1.414 * 180 / self.cl));
        self.c2 = self.b1
        self.c3 = - self.a1**2
        self.c1 = 1 - self.c2 - self.c3;
                
    def algoFunc(self,px):
        #clean up
        hplst=[]
        filtlst=[]
        nrflst=[]
        quolst=[]
        shortquolst=[]
        peaklst=[]
        pricelst=[]
        
        self.quolst = []
        self.shortquolst = []
        self.nrflst = []


        for index in range(0, len(px)):
            price = px[index]
            
            hplst.append(0.)
            filtlst.append(0.)
            peaklst.append(0.)
            self.quolst.append(0.)
            self.shortquolst.append(0.)
            self.nrflst.append(0.)
            pricelst.append(price) #?
        
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
            hplst[index] = hp0
                
            filt = self.EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2);
            filtlst[index] = filt
        
            #fast attack            
            peak0 = peak1*0.991
            
            af = abs(filt)
            if af > peak0:
                peak0 = af
                
            peaklst[index] = peak0
            
            NormRoofingFilter = filt / peak0;
            Quotient1 = (NormRoofingFilter + self.k1) / (self.k1 * NormRoofingFilter + 1);
            Quotient2 = (NormRoofingFilter + self.k2) / (self.k2 * NormRoofingFilter + 1);
            
            #print index,len(self.quolst)
            self.quolst[index] = Quotient1
            self.shortquolst[index] = Quotient2            
            self.nrflst[index] = NormRoofingFilter # who use it?
            
            #must be placed before trigger signal(to avoid buying ahead)
            #move to strategy           
            '''
            prevQuotient = self.quolst[index-1]
            prevShortQuo = self.shortquolst[index-1]
            
            # trading signal
            if prevQuotient<0 and Quotient1>=0:
                #print "quotient buy@",index
                self.tradesup.buyorder(self.stname)
                    
            if prevShortQuo>0 and Quotient2<=0:
                #print "quotient sell@",index
                self.tradesup.sellorder(self.stname)
            '''
        pass


    #main process routine
    def runIndicator(self,symbol,ohlc,param={}):
        self.setupParam(param)     
        self.close_px = ohlc['Adj Close']
        self.algoFunc(self.close_px)     
