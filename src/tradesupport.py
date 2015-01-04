import numpy as np
import pandas

class Trade:
    def setup(self,ohlc_px,deposit):
        self.ohlc_px=ohlc_px
        self.deposit = deposit
        self.shares = 0
        self.ser_orders = []
        self.ser_orderdate = []
        self.ser_pnl = []
        self.ser_price = []
        self.ser_dayvalue = []
        self.total_order = 0
        self.profit_order = 0
        self.loss_order = 0
        self.trancost = 0
        self.dailyvalue=[]
        self.buyFlag=False
        self.order=0
        self.offset=0
        self.verbose = True
        if self.verbose==True:
            print "========== S E T U P ====================="
  
    def getMeanpx(self,index):
        return (self.ohlc_px['Open'][index]+self.ohlc_px['Close'][index]+self.ohlc_px['High'][index]+self.ohlc_px['Low'][index])/4

    def getBuyPower(self):
        return self.deposit/(1+0.0025*1.07)

    def getBuyComm(self,trancost):
        comm = trancost * 0.0025 * 1.07 
        return comm
    
    def getSellComm(self,trancost):
        comm = trancost*(0.0025+0.0000174)*1.07
        return comm
    
    def processData(self,index):
        if self.order==1:
            self.order=0            
            self.buyFlag = True

            #find a tradable price 
            meanpx = self.getMeanpx(index)
            buypower = self.getBuyPower()
            
            self.shares = int(buypower/meanpx)
            self.trancost = self.shares*meanpx + self.getBuyComm(self.shares*meanpx)
            self.deposit = self.deposit-self.trancost
            if self.offset==0:
                self.offset = index
                
            datelb = self.ohlc_px.index[index].to_pydatetime()

            self.ser_orders.append('buy')
            self.ser_orderdate.append(self.ohlc_px.index[index])
            self.ser_pnl.append(None)
            self.ser_price.append(meanpx)
            if self.verbose==True:
                print datelb," buy ",self.shares,"@",meanpx,(",commission=%.3f"%self.getBuyComm(self.shares*meanpx)),",remain=%.3f"%(self.deposit)
                #str = datelb," buy ",self.shares,"@",meanpx,",commission=%.3f",self.getBuyComm(self.shares*meanpx),",remain=%.3f",self.deposit
        elif self.order==2:
            self.order=0
            meanpx = self.getMeanpx(index)
            sellcomm = self.getSellComm(self.shares*meanpx)
            trancost = self.shares*meanpx-sellcomm
            self.deposit = self.deposit+trancost  #pricelst[index]
            shares = self.shares
            self.shares = 0
            #self.sellorder.append(index)
            self.buyFlag = False

            datelb = self.ohlc_px.index[index].to_pydatetime()
            
            self.ser_orders.append('sell')
            self.ser_orderdate.append(self.ohlc_px.index[index])
            
            pnl = trancost - self.trancost
            self.ser_pnl.append(pnl)
            self.ser_price.append(meanpx)
            
            if pnl>=0:
                self.profit_order+=1
            else:
                self.loss_order+=1
            if self.verbose==True:
                print datelb," sell ",shares,"@",meanpx,",commission=%.3f"%sellcomm,",remain=%.3f"%self.deposit
        return
        
    def buyorder(self):
        if self.buyFlag==False:
            self.order=1
            #self.buyFlag=True
        return
    
    def sellorder(self):
        if self.buyFlag==True:
            self.order=2
            #self.buyFlag=False
        return
 
    def setDailyValue(self,index):
        # day to day value
        self.dailyvalue.append(self.deposit+self.shares*self.ohlc_px['Adj Close'][index])
        
    def getDailyValue(self):
        self.dy = pandas.DataFrame({'dayvalue':self.dailyvalue},index=self.ohlc_px.index.values)
        #print self.dy
        return self.dy
  
    def getTradeReport(self):
        return pandas.DataFrame({'order':self.ser_orders,'price':self.ser_price,'pnl':self.ser_pnl},index=self.ser_orderdate)

    def getFirstTradeIdx(self):
        return self.offset
    
    def getProfitOrderNum(self):
        return self.profit_order

    def getLossOrderNum(self):
        return self.loss_order
        
    # max drawdown    
    #print "Max draw down %.2f %%" % (maxdd(df['dayvalue'][offset:])*100)            
    def getMaxdd(self):
        ser = self.dy['dayvalue'][self.offset:]
        # only compare each point to the previous running peak
        # O(N)
        running_max = pandas.expanding_max(ser)
        ddpct =  (ser - running_max)/running_max
        return abs(ddpct.min())
        
        #cur_dd = ser - running_max
        #print ser
        #for item in running_max.values:
        #for index in range(0, len(running_max)):
        #    print ser[index],running_max[index],ddpct[index]
        #return min(0, cur_dd.min()) 
        
    def basefacts(self,bm_returns,sgy_returns):
        covmat = np.cov(bm_returns,sgy_returns)
    
        beta = covmat[0,1]/covmat[1,1]
        alpha = np.mean(sgy_returns)-beta*np.mean(bm_returns)
        
        
        ypred = alpha + beta * bm_returns
        SS_res = np.sum(np.power(ypred-sgy_returns,2))
        SS_tot = covmat[0,0]*(len(bm_returns)-1) # SS_tot is sample_variance*(n-1)
        r_squared = 1. - SS_res/SS_tot
        # 5- year volatiity and 1-year momentum
        volatility = np.sqrt(covmat[0,0])
        momentum = np.prod(1+sgy_returns.tail(12).values) -1
        
        # annualize the numbers
        prd = 12. # used monthly returns; 12 periods to annualize
        alpha = alpha*prd
        volatility = volatility*np.sqrt(prd) 
        #print beta,alpha, r_squared, volatility, momentum      
        return dict({'alpha':alpha,'beta':beta,'volatility':volatility,'momentum':momentum})
    



        

