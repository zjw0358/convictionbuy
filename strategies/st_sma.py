'''
calculate simple moving average
'''
#import pandas
#from collections import OrderedDict
from ind_ma import ind_ma
from st_pattern import StrategyPattern

class st_sma(ind_ma):
    def usage(self):
        return "px>ma200"


    def setupParam(self,param):
        return
        
   
    def runIndicator(self,symbol,ohlc,param={}):
        ind_ma.runIndicator(self,symbol,ohlc,param)
        self.algoStrategy()
        pass
    
    def algoStrategy(self):
        # price cross above MA10 and crosee below MA10
        sp = StrategyPattern()
        sp.initData(self.close_px, self.ma10, 50)
        self.ind['sma10_buy'] = sp.crossAbove()
        self.ind['sma10_sell'] = sp.crossBelow()
        
        if (self.ma50):
            sp.initData(self.close_px, self.ma50, 50)
            buy = sp.crossAbove()
            sell = sp.crossBelow()
            if (buy < sell):
                self.ind['ma50_buy'] = str(buy)
#                self.ind['ma50_sell'] = ""
            elif ( buy > sell):
                self.ind['ma50_sell'] = str(sell)
                
            #self.ind['ma50_buy'] = sp.crossAbove()
            #self.ind['ma50_sell'] = sp.crossBelow()
            
        #MA50 cross MA200
        #print "checking ma50 vs ma200",(not self.ma50),(not self.ma200)
        #too lag, how about px cross MA50
        '''
        if (self.ma50 and self.ma200):
            sp.initData(self.ma50, self.ma200, 200)
            self.ind['ma50_200_buy'] = sp.crossAbove()
            self.ind['ma50_200_sell'] = sp.crossBelow()
        '''    
        pass
    def runScan(self,table):
        return table
