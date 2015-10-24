'''
backtest module
'''
class Ordermg:
    def beginTrade(self):
        self.position = ""
        self.power = 10000.
        self.gainloss = 0.
        self.shares = 0.
        self.pendingOrder = ""
        self.totalTrade = 0
        self.win = 0

    def endTrade(self,row):
        avgpx = (row['High']+row['Low']+row['Close']+row['Open'])/4
        self.closeTrade(float(avgpx))        
        #print self.shares * avgpx + self.power
        print self.totalTrade,float(self.win)/self.totalTrade, self.gainloss, self.gainloss/self.power
        
    def closeTrade(self,avgpx):
        gl = self.shares * avgpx - self.power
        self.totalTrade += 1
        #print gl
        if gl>0:
            self.win += 1
        self.gainloss += gl
        self.shares = 0 
                    
    def procPendingOrder(self,row,index):  
        #print row      
        if (self.pendingOrder != ""):
            avgpx = (row['High']+row['Low']+row['Close']+row['Open'])/4
            #print avgpx
            if (self.pendingOrder == "buy"):
                print "buy@",index
                self.shares = self.power / avgpx
                self.position = "buy"
            elif (self.pendingOrder == "sell"):
                '''
                gainloss = self.shares * avgpx - self.power
                self.totalTrade += 1
                if (gainloss>0):
                    self.win += 1
                self.gainloss += gainloss
                self.shares = 0 
                '''
                print "sell@",index
                self.closeTrade(float(avgpx))
                self.position = "sell"             
            self.pendingOrder = ""   
        pass
        
    def buyorder(self):
        if (self.position != "buy"):
            self.pendingOrder = "buy"
        pass  
        
    def sellorder(self):
        if (self.position == "buy"):
            self.pendingOrder = "sell"
        pass
    
class ms_backtest:
    def runBackTest(self,ohlc):
        print ohlc
        ordermg = Ordermg()
        ordermg.beginTrade()
        print "==============================="
        for row_index, row in ohlc.iterrows():
            ordermg.procPendingOrder(row,row_index)
            if row['buy'] =="buy":
                ordermg.buyorder()
            elif row['sell'] =="sell":
                ordermg.sellorder()
        lastRow = ohlc.tail(1)
        ordermg.endTrade(lastRow)
        pass