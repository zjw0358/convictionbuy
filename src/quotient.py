import matplotlib.pyplot as plt
import math

'''need additional 100 bars to stabilize the chart'''

cutoffLength = 20;
k1 = 0.9;
k2 = 0.4
alpha1 = (math.cos(math.radians(0.707*360 / 100)) + math.sin (math.radians(0.707*360 / 100)) - 1) / math.cos(math.radians(0.707*360 / 100))
a1 = math.exp(-1.414 * math.pi / cutoffLength);
b1 = 2 * a1 * math.cos(math.radians(1.414 * 180 / cutoffLength));
c2 = b1
c3 = - a1*a1
c1 = 1 - c2 - c3;
    
def EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2,cutoffLength):
    '''cutoffLength = 10;'''
    #a1 = math.exp(-1.414 * math.pi / cutoffLength);
    #global a1
    #b1 = 2 * a1 * math.cosh(1.414 * math.pi / cutoffLength);
    
    
    filt =  c1 * (hp0 + hp1) / 2 + c2 * filt1 + c3 * filt2;
    return filt


def quotient(pricelst,datelst):    
    hplst=[]
    filtlst=[]
    nrflst=[]
    quolst=[]
    shortquolst=[]
    peaklst=[]
    buyorder=[]
    sellorder=[]
    
    print "alpha1,",alpha1
    print "(1 - alpha1 / 2)*(1 - alpha1 / 2),",(1 - alpha1 / 2)*(1 - alpha1 / 2) 
    print "a1,",a1
    print "b1,",b1
    print "c1,",c1
    print "c2,",c2
    print "c3,",c3
    
    
    buyFlag = False
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
       
        hp0 = (1 - alpha1 / 2)*(1 - alpha1 / 2) * (price - 2 * price1 + price2) + 2 * (1 - alpha1) * hp1 - (1 - alpha1)*(1 - alpha1) * hp2;
        hplst[index]=hp0
        
                  
        filt = EhlersSuperSmootherFilter(hp0,hp1,filt1,filt2,cutoffLength);
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
        Quotient1 = (NormRoofingFilter + k1) / (k1 * NormRoofingFilter + 1);
        Quotient2 = (NormRoofingFilter + k2) / (k2 * NormRoofingFilter + 1);
        quolst[index]=Quotient1
        shortquolst[index]=Quotient2
        nrflst[index]=NormRoofingFilter
        
        #buy order 
        prevQuotient = quolst[index-1]
        prevShortQuo = shortquolst[index-1]
        if prevQuotient<0 and Quotient1>=0 and buyFlag==False:
            #buydate = datelst[index]
            buyorder.append(index)
            buyFlag = True
        if prevShortQuo>0 and Quotient2<=0 and buyFlag==True:
            #selldate = datelst[index]
            sellorder.append(index)
            buyFlag = False
        #debug
        #print index,hp0,filt,peak0,NormRoofingFilter,Quotient1
        
        print datelst[index],pricelst[index],hplst[index],filtlst[index],peaklst[index],nrflst[index],quolst[index]
        
    print "return quolst=",len(quolst)
    print "buyorder=",buyorder
    print "sellorder=",sellorder
    backtest(buyorder,sellorder,pricelst,datelst)
    return quolst
    
def backtest(buyorder,sellorder,pricelst,datelst):
    totalpnl=0.
    orderlen = min(len(buyorder),len(sellorder))
    for i in range(0, orderlen):
        buyid = buyorder[i]
        sellid = sellorder[i]
        pnl = pricelst[sellid] - pricelst[buyid]
        totalpnl+=pnl
        print datelst[buyid]," buy@",pricelst[buyid]," ",datelst[sellid]," sell@",pricelst[sellid]
        
    print "total pnl=", totalpnl
    if orderlen<len(buyorder):
        buyid = buyorder[orderlen]
        print datelst[buyid]," buy@",pricelst[buyid]," current price=",pricelst[-1]," ",datelst[-1]
