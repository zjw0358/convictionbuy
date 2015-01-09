import pandas
import time


class SimuTable:
    def __init__(self,support):
        self.columns = ['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade','bh_profit'] #,
        self.besttable = pandas.DataFrame(columns=self.columns) 
        self.firstBestResultAdded = False
        self.support = support
        self.outputpath="../result/"
        self.bestperf=0
        #self.bestdv# = pandas.DataFrame(columns='dayvalue')
        print "SimuTable initialized"

        return
    def setName(self,name):
        self.name = name
         
  #bm=benchmark px 
    def setupSymbol(self,symbol,bm):
        self.symbol=symbol
        self.bm=bm
        #columns = ['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade'] #,
        #dftbl = pandas.DataFrame(columns=columns,index=length) 
        self.symtable = pandas.DataFrame(columns=self.columns) 
    
    #param - strategy parameter    
    #df - day value
    def addSymbolResult(self,param,df):
        firstTradeIdx = self.support.getFirstTradeIdx()
        rtbm = self.bm[firstTradeIdx:].resample('M',how='last')
        bm_returns = rtbm.pct_change()        
        bm_returns = bm_returns.dropna()
        rtsgy = df['dayvalue'][firstTradeIdx:].resample('M',how='last')
        sgy_returns = rtsgy.pct_change()
        sgy_returns=sgy_returns.dropna()
        
        bhprofit = self.support.getBHprofit() #buy&hold profit
        # get base facts,alpha,beta,volatility,etc
        dct = self.support.getBasefacts(bm_returns,sgy_returns)
        

        tradereport = self.support.getTradeReport()
        lastTrade = tradereport.tail(1).to_string(header=False)
        print tradereport
        perfdata = tradereport['pnl'].sum()
        if perfdata>self.bestperf:
            self.bestperf = perfdata
            self.bestdv=df #this is best day value data frame
        
        d0 = {'symbol':self.symbol,'param':param,'alpha':dct['alpha'],'beta':dct['beta'],'perf':perfdata,\
        'max_drawdown':self.support.getMaxdd(),'profit_order':self.support.getProfitOrderNum(),\
        'loss_order':self.support.getLossOrderNum(),'last_trade':lastTrade,'bh_profit':bhprofit}
        
        # add new row with external index start from 1,2,3
        self.symtable.loc[len(self.symtable)+1]=d0
        
    def makeSymbolReport(self):
        sortTable = self.symtable.sort_index(by='perf',ascending=False)
        filename=self.outputpath+self.symbol+'_'+self.name+time.strftime('_%Y-%m-%d.csv',time.localtime(time.time()))
        try:
            sortTable.to_csv(filename,sep=',')
        except:
            print "exception when write to csv ",filename
        
        print "================================================================"
        print self.symbol + " all simulation results:"
        print sortTable
        print "================================================================"
        

        bestrow = sortTable.head(1).iloc[0]        
        self.besttable.loc[len(self.besttable)+1]=bestrow
        
    def makeBestReport(self):
        sortTable = self.besttable.sort_index(by='perf')
        filename=self.outputpath+self.name+"_best_"+time.strftime('%Y-%m-%d.csv',time.localtime(time.time()))
        sortTable.to_csv(filename,sep=',')
        if not sortTable.empty:
            print "================================================================"
            print self.name + " portfolio best performance:"
            print sortTable
            print "================================================================"
            
    def getBestDv(self):
        #print "bestdv=",self.bestdv
        return self.bestdv