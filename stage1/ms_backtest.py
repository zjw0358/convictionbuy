'''
backtest module
'''
import pandas

class Ordermg:
    def beginTrade(self):
        self.position = ""
        self.power = 10000.
        self.gainloss = 0.
        self.shares = 0.
        self.pendingOrder = ""
        self.totalTrade = 0
        self.win = 0
        self.winrate = 0.
        self.gainreturn = 0.
        self.maxgainp = 0.
        self.maxlossp = 0.
        
    def endTrade(self,row,index):
        avgpx = (row['High']+row['Low']+row['Close']+row['Open'])/4
        self.closePos(index,float(avgpx),row['Close'],row['Adj Close'])        
        if (self.totalTrade==0):
            self.winrate = 0
        else:
            self.winrate = round(float(self.win)/self.totalTrade,2)
        self.gainreturn = round(self.gainloss/self.power,2)
        print "================================"
        print "Total Trade",self.totalTrade
        print "Win Rate%",round(self.winrate*100,2)
        print "Gain/Loss",self.gainloss
        print "Return%",round(self.gainreturn*100,2)
        print "Max Gain%",round(self.maxgainp,2)
        print "Max Loss%",round(self.maxlossp,2)
        print "================================"
        #print self.totalTrade,self.winrate,self.gainloss, self.gainreturn, self.maxgainp, self.maxlossp
        
    # close a position
    def closePos(self,index,avgpx,close,adjclose):
        if (self.shares > 0):  
            if ((abs(avgpx-adjclose)/adjclose*100)>5):
                #check if stock split
                ratio = adjclose / close
                avgpx = avgpx * ratio
                          
            gl = self.shares * avgpx - self.power
            self.totalTrade += 1
            if gl>0:
                self.win += 1
                gp = gl*100/self.power
                self.maxgainp = max(gp,self.maxgainp)
            else:
                gp = gl*(-100)/self.power
                self.maxlossp = max(gp,self.maxlossp)
            self.gainloss += gl
            self.shares = 0
            self.position = "sell"
            print "sell@",index,"gain=",round(gl,2)
            
    def openPos(self,index,avgpx,close,adjclose):
        if ((abs(avgpx-adjclose)/adjclose*100)>5):
            #check if stock split
            ratio = adjclose / close
            avgpx = avgpx * ratio
        
        print "buy@",index,"px=",avgpx
        self.shares = self.power / avgpx
        self.position = "buy"
        pass    
                
    def procPendingOrder(self,row,index):       
        avgpx = (row['High']+row['Low']+row['Close']+row['Open'])/4
        if (self.pendingOrder != ""):

            #print avgpx
            if (self.pendingOrder == "buy"):
                self.openPos(index,avgpx,row['Close'],row['Adj Close'])
                                
            elif (self.pendingOrder == "sell"):
                '''
                gainloss = self.shares * avgpx - self.power
                self.totalTrade += 1
                if (gainloss>0):
                    self.win += 1
                self.gainloss += gainloss
                self.shares = 0 
                '''
                self.closePos(index,avgpx,row['Close'],row['Adj Close'])

            self.pendingOrder = ""
        else:
            #self.stopwin(avgpx,index)
            #self.stoploss(avgpx,index)
            pass
        pass
        
    def stopwin(self, avgpx,index):
        stopwin = 2
        if ((avgpx*self.shares - self.power) *100 / self.power ) > stopwin :
            self.closePos(avgpx,index)        
        pass
        
    def stoploss(self,avgpx,index):
        stoploss = 5
        if ((avgpx*self.shares - self.power) < (self.power * stoploss /100)) :
            self.closePos(avgpx,index)     
        pass
        
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
    def __init__(self):
        self.symbols = []
        self.totalTrade = []
        self.winrate = []
        self.gain=[]
        self.gainreturn = []
        pass
        
    def runBackTest(self,sym,ohlc):
        print ohlc
        ordermg = Ordermg()
        ordermg.beginTrade()
        print "==============================="
        for row_index, row in ohlc.iterrows():
            ordermg.procPendingOrder(row,row_index)
            '''
            if row['buy'] =="buy":
                ordermg.buyorder()
            elif row['sell'] =="sell":
                ordermg.sellorder()
            '''
            if row['signal'] =="buy":
                ordermg.buyorder()
            elif (row['signal'] =="sell" or row['signal'] =="close"):
                ordermg.sellorder()
            
        #lastRow = ohlc.tail(1).value()
        lastRow = ohlc.iloc[-1] 
        lastidx = ohlc.index[-1]
        ordermg.endTrade(lastRow,lastidx)
        
        self.symbols.append(sym)
        self.totalTrade.append(ordermg.totalTrade)
        self.winrate.append(ordermg.winrate)
        self.gain.append(ordermg.gainloss)
        self.gainreturn.append(ordermg.gainreturn)        
        pass
        
    def getBackTestResult(self):
        return pandas.DataFrame({'symbol':self.symbols,'total trade':self.totalTrade,'win rate':self.winrate,'gain':self.gain,'return%':self.gainreturn},columns=\
        ['symbol','total trade','win rate','gain','return%'])
        pass
        