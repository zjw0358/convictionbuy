'''
backtest module
'''
import pandas
import datetime

class Ordermg:
    def beginTrade(self, verbose):
        self.verbose = verbose
        self.position = ""
        self.power = 10000.
        self.gainloss = 0.
        self.shares = 0.
        self.pendingOrder = ""
        self.totalTrade = 0
        self.win = 0
        self.winrate = ""
        self.gainreturn = 0.
        self.maxgainp = 0.
        self.maxlossp = 0.
        
    def endTrade(self, row, index):
        avgpx = (row['High'] + row['Low'] + row['Close'] + row['Open'])/4
        self.closePos(index, float(avgpx), row['Close'], row['Adj Close'])
        if (self.totalTrade == 0):
            self.winrate = 0
        else:
            self.winrate = round(float(self.win*100.0)/self.totalTrade, 2)

        self.gainreturn = round(self.gainloss*100.0/self.power, 2)
        self.maxgainp = round(self.maxgainp, 2)
        self.maxlossp = round(self.maxlossp, 2)
        #self.maxgainstr = "%.2f %%" % round(self.maxgainp, 2)
        #self.maxlossstr = "%.2f %%" % round(self.maxlossp, 2)
        '''
        print "================================"
        print "Total Trade", self.totalTrade
        print "Win Rate%", self.winrate #round(self.winrate*100,2)
        print "Gain/Loss", self.gainloss
        print "Return%", self.gainreturn #round(self.gainreturn*100,2)
        print "Max Gain%", "%.2f %%" % round(self.maxgainp, 2)
        print "Max Loss%", "%.2f %%" % round(self.maxlossp, 2)
        print "================================"
        '''
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
            if self.verbose > 0:
                print "%-8s%04d%-10s%.2f%-10s%.2f" % ("sell@", index, ",px=", round(avgpx,2), ",gain=", round(gl, 2))
            
    def openPos(self, index, avgpx, close, adjclose):
        if ((abs(avgpx-adjclose)/adjclose*100)>5):
            #check if stock split
            ratio = adjclose / close
            avgpx = avgpx * ratio

        if self.verbose > 0:
            #print "%-8s%04d%-10s%.2f" % ("buy@", index, ",px=", avgpx)
            print "%-8s%14s%-10s%.2f" % ("buy@", index, ",px=", avgpx)

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
                self.closePos(index, avgpx, row['Close'], row['Adj Close'])

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
        self.beginBackTest()
        pass

    def beginBackTest(self):
        self.symbols = []
        self.totalTrade = []
        self.winrate = []
        self.win = []
        self.gain=[]
        self.gainreturn = []
        self.maxgain = []
        self.maxloss = []
        #self.btdf = pandas.DataFrame(columns=['symbol', 'total trade', 'winrate', 'gain_loss', 'return'])
        pass

    def combineSignal(self, ohlc, buydct, selldct):
        flag = True
        for key in buydct:
            if key not in ohlc:
                flag = False

        for key in selldct:
            if key not in ohlc:
                flag = False

        if not flag:
            ohlc['signal'] = ['']*len(ohlc)
            return

        def cleardct(dct):
            for key in dct:
                dct[key] = 0
            pass


        def buyspread(dct):
            minv = 100000
            maxv = 0
            spread = 6
            for key in dct:
                minv = min(dct[key], minv)
                maxv = max(dct[key], maxv)
            if (maxv-minv) > spread:
                return False
            else:
                return True
            pass

        #print buydct,selldct
        cleardct(buydct)
        cleardct(selldct)

        signallst = []
        idx = 1
        for row_index, row in ohlc.iterrows():
            signal = ""
            for bs in buydct:
                if row[bs] == "buy":
                    buydct[bs] = idx

            for ss in selldct:
                if row[ss] == "sell":
                    selldct[ss] = 1

            buy_flag = True
            for bs in buydct:
                if buydct[bs] == 0:
                    buy_flag = False


            all_sell_flag = True
            one_sell_flag = False
            for ss in selldct:
                if selldct[ss] != 1:
                    all_sell_flag = False
                else:
                    one_sell_flag = True

            if one_sell_flag:
                # reset buydict
                buy_flag = False
                for bs in buydct:
                    buydct[bs] = 0

            if one_sell_flag:
                signal = "sell"
                for ss in selldct:
                    selldct[ss] = 0

            if buy_flag:
                if buyspread(buydct):
                    signal = "buy"
                for key in buydct:
                    buydct[key] = 0
            idx += 1
            signallst.append(signal)
        ohlc['signal'] = signallst
        pass

    def runBackTest(self, sym, ohlc, verbose=0):
        self.verbose = verbose
        ordermg = Ordermg()
        ordermg.beginTrade(verbose)
        if verbose > 0:
            print "==============================="
            print "\t", sym, " trade logs"
            print "===============================\n"


        for row_index, row in ohlc.iterrows():
            ordermg.procPendingOrder(row, row_index)
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
        ordermg.endTrade(lastRow, lastidx)
        
        self.symbols.append(sym)
        self.totalTrade.append(ordermg.totalTrade)
        self.winrate.append(ordermg.winrate)
        self.win.append(ordermg.win)
        self.gain.append(ordermg.gainloss)
        self.gainreturn.append(ordermg.gainreturn)
        self.maxgain.append(ordermg.maxgainp)
        self.maxloss.append(ordermg.maxlossp)

        pass
        
    def printBackTestResult(self):
        df = pandas.DataFrame({'symbol': self.symbols, 'total trade': self.totalTrade, 'win trade': self.win, 'win rate%': self.winrate,
                                 'gain': self.gain, 'return%': self.gainreturn, 'maxgain%': self.maxgain, 'maxloss%':
                                 self.maxloss},
                                columns = ['symbol', 'total trade', 'win trade', 'win rate%', 'gain', 'return%', 'maxgain%', 'maxloss%'])
        df = df[df['total trade']!=0]
        print "==============================="
        print df
        if len(df)==0:
            return df
        tt = df['total trade'].sum()
        wt = df['win trade'].sum()
        wr = "%.2f %%" % (wt * 100.0 / tt)
        tga = df['gain'].sum()
        trt = df['return%'].sum()
        mg = df['maxgain%'].max()
        ml = df['maxloss%'].max()

        sumdf = pandas.DataFrame({'total trade': [tt], 'win trade': [wt], 'win rate%': [wr],
                                 'total gain': [tga], 'avg gain': [tga/tt], 'total return%': [trt],
                                  'avg return%': [trt/tt], 'maxgain%': [mg], 'maxloss%': [ml]},
                                 columns=['total trade', 'win trade', 'win rate%', 'total gain', 'avg gain',
                                          'total return%', 'avg return%', 'maxgain%', 'maxloss%'])
        print "..............................."
        print sumdf
        # save to csv
        ts = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        outputFn = "../result/backtest_" + ts + '.csv'
        sumfn =  "../result/backtest_" + ts + '_summary.csv'
        try:
            df.to_csv(outputFn, sep=',', index=False)
            print "Finish wrote to ", outputFn
            sumdf.to_csv(sumfn, sep=',', index=False)
            print "Finish wrote to ", sumfn

        except:
            print "exception when write to csv ", outputFn, sumfn


        return df