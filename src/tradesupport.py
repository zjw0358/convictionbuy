import numpy as np
import pandas

class Trade:
    def __init__(self):
        self.stgyorder = {}

    # call this when run a new strategy      
    def setup(self,symbol, ohlc_px,deposit = 10000):
        self.verbose = True
        if self.verbose == True:
            print "========== T R A D I N G L O G @",symbol, "====================="

        self.ohlc_px = ohlc_px
        self.deposit = deposit
        self.initialdeposit = deposit
        
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
        self.dailyvalue = []
        self.buyopen = False
        self.firstTradeIdx = 0  #reset first trade index
        for strategy in self.stgyorder:
            self.stgyorder[strategy] = ''

  
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

    def getLastSellPrice(self):
        return self.ser_price[-1]
                
    #TODO, each strategy has different weight
    #some strategy are dominant
    def processData(self,index):
        #require all strategy give 'buy' signal
        buyFlag = True
        for strategy in self.stgyorder:
            if self.stgyorder[strategy]!='b':
                buyFlag=False
                break
                
        sellFlag=False
        
        #as long as one strategy ask for selling.
        for strategy in self.stgyorder:
            if self.stgyorder[strategy]=='s':
                sellFlag=True 
                break

                                      
        if buyFlag==True and self.buyopen==False:
            #buy
            #find a tradable price 
            meanpx = self.getMeanpx(index)
            buypower = self.getBuyPower()
            
            self.shares = int(buypower/meanpx)
            self.trancost = self.shares*meanpx + self.getBuyComm(self.shares*meanpx)
            self.deposit = self.deposit-self.trancost
            if self.firstTradeIdx==0:
                self.firstTradeIdx = index
                
            datelb = self.ohlc_px.index[index].to_pydatetime()

            self.ser_orders.append('buy')
            self.ser_orderdate.append(self.ohlc_px.index[index])
            self.ser_pnl.append(0)
            self.ser_price.append(meanpx)
            if self.verbose==True:
                print datelb," buy ",self.shares,"@",meanpx,(",commission=%.3f"%self.getBuyComm(self.shares*meanpx)),",remain=%.3f"%(self.deposit)
                #str = datelb," buy ",self.shares,"@",meanpx,",commission=%.3f",self.getBuyComm(self.shares*meanpx),",remain=%.3f",self.deposit
            
            # open an order
            self.buyopen=True
            # clean all 'buy' signal
            
            
        elif sellFlag==True and self.buyopen==True:
            meanpx = self.getMeanpx(index)
            sellcomm = self.getSellComm(self.shares*meanpx)
            trancost = self.shares*meanpx-sellcomm
            self.deposit = self.deposit+trancost  #pricelst[index]
            shares = self.shares
            self.shares = 0

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
                
            #close the order
            self.buyopen=False
            
        '''if self.order==1:
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
            self.ser_pnl.append(0)
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
                print datelb," sell ",shares,"@",meanpx,",commission=%.3f"%sellcomm,",remain=%.3f"%self.deposit'''
        
        
    def buyorder(self,stname):
        if stname in self.stgyorder:
            self.stgyorder[stname]='b'
        return
    
    def sellorder(self,stname):
        if stname in self.stgyorder:
            self.stgyorder[stname]='s'
        
    def holdorder(self,stname):
        if stname in self.stgyorder:
            self.stgyorder[stname]='h'
        
    def calcDailyValue(self,index):
        # day to day value
        self.dailyvalue.append(self.deposit+self.shares*self.ohlc_px['Adj Close'][index])
        
    def getDailyValue(self):
        return self.dy
        
    def createDailyValueDf(self):
        self.dy = pandas.DataFrame({'dayvalue':self.dailyvalue},index=self.ohlc_px.index.values)        
        self.tradeRept = pandas.DataFrame({'order':self.ser_orders,'price':self.ser_price,'pnl':self.ser_pnl},index=self.ser_orderdate)
        
    def setDailyValueDf(self,dy):
        self.dy=dy

    def setTradeReportWithBestPerf(self, rept):
        self.tradeRept = rept
        
    def getTradeReport(self):
        return self.tradeRept
    
    #this is set by simutable, replace the current first trade idx with best performance first trade idx
    def setFirstTradeIdxWithBestPerf(self,idx):
        self.firstTradeIdx = idx
        
    def getFirstTradeIdx(self):
        return self.firstTradeIdx

    def getFirstTradeDate(self):
        d = self.ohlc_px.index[self.firstTradeIdx]
        return d
        
    def getBHprofit(self):
        #print "first trade date=",self.getFirstTradeDate()
        buypx = self.ohlc_px['Close'][self.firstTradeIdx]
        lastpx = self.ohlc_px['Close'][-1]

        bhp = round(self.initialdeposit/buypx*lastpx - self.initialdeposit,2)
        #print "buy=",buypx,"sell=",lastpx,"profit=",bhp
        return bhp
        
    def getProfitOrderNum(self):
        return self.profit_order

    def getLossOrderNum(self):
        return self.loss_order
        
    # max drawdown    
    #print "Max draw down %.2f %%" % (maxdd(df['dayvalue'][offset:])*100)            
    def getMaxdd(self):
        ser = self.dy['dayvalue'][self.firstTradeIdx:]
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
        
    def getBasefacts(self,bmr,sgyr): #bm_returns,sgy_returns):
        #print bm_returns,sgy_returns
        minidx=min(len(bmr),len(sgyr))
        bm_returns=bmr[-minidx:]
        sgy_returns=sgyr[-minidx:]
        #print bm_returns,sgy_returns        
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

    #register strategy name
    def addStrategy(self,stname):  
        self.stgyorder[stname]='' #''-default,'b'-buy,'s'-sell
        


        

