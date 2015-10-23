'''
backtest module
'''
class Ordermg:
    def beginTrade(self):
        self.position = ""
        self.power = 10000.
        self.shares = 0.
        self.pendingOrder = ""
        
    def endTrade(self,row):
        avgpx = (row['High']+row['Low']+row['Close']+row['Open'])/4
        print self.shares * avgpx + self.power
                
    def procPendingOrder(self,row):  
        #print row      
        if (self.pendingOrder != ""):
            avgpx = (row['High']+row['Low']+row['Close']+row['Open'])/4
            if (self.pendingOrder == "buy"):
                #print "buy"
                self.shares = self.power / avgpx
                self.power = 0
                self.position = "buy"
            elif (self.pendingOrder == "sell"):
                self.power = self.shares * avgpx
                self.shares = 0 
                self.position = "sell"                
            self.pendingOrder = ""   
        pass
        
    def buyorder(self):
        if (self.position != "buy"):
            self.pendingOrder = "buy"
        pass  
        
    def sellorder(self):
        if (self.position != "buy"):
            self.pendingOrder = "sell"
        pass
    
class ms_backtest:
    def runBackTest(self,ohlc):
        print ohlc
        ordermg = Ordermg()
        ordermg.beginTrade()
        for row_index, row in ohlc.iterrows():
            ordermg.procPendingOrder(row)
            if row['buy'] =="buy":
                ordermg.buyorder()
            elif row['buy'] =="sell":
                ordermg.sellorder()
        lastRow = ohlc.tail(1)
        ordermg.endTrade(lastRow)
        pass