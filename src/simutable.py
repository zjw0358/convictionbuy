import pandas
import time


class SimuTable:
    def __init__(self,support):
        self.columns = ['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade','bh_profit','mark'] #,
        self.besttable = pandas.DataFrame(columns=self.columns) 
        self.firstBestResultAdded = False
        self.tradesup = support
        self.outputpath="../result/"
        self.bestperf=-10000000
        self.bestperfFirstTradeIdx=0
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
    def addOneTestResult(self,param,df,minfo=""):
        firstTradeIdx = self.tradesup.getFirstTradeIdx()
        rtbm = self.bm[firstTradeIdx:].resample('M',how='last')
        bm_returns = rtbm.pct_change()        
        bm_returns = bm_returns.dropna()
        rtsgy = df['dayvalue'][firstTradeIdx:].resample('M',how='last')
        sgy_returns = rtsgy.pct_change()
        sgy_returns=sgy_returns.dropna()
        
        bhprofit = self.tradesup.getBHprofit() #buy&hold profit
        # get base facts,alpha,beta,volatility,etc
        dct = self.tradesup.getBasefacts(bm_returns,sgy_returns)
        

        tradereport = self.tradesup.getTradeReport()
        if tradereport.empty:
            lastTrade = "empty"
        else:
            lastTrade = tradereport.tail(1).to_string(header=False)
        
        #find the best performance
        perfdata = tradereport['pnl'].sum()
        print tradereport,"PnL=",perfdata,"B/H profit=",bhprofit
        if perfdata>self.bestperf:
            self.bestperf = perfdata
            self.bestdv = df #this is best day value data frame
            self.bestperfFirstTradeIdx = firstTradeIdx
            self.bestperfRept = self.tradesup.getTradeReport()
        
        d0 = {'symbol':self.symbol,'param':param,'alpha':dct['alpha'],'beta':dct['beta'],'perf':perfdata,\
        'max_drawdown':self.tradesup.getMaxdd(),'profit_order':self.tradesup.getProfitOrderNum(),\
        'loss_order':self.tradesup.getLossOrderNum(),'last_trade':lastTrade,'bh_profit':bhprofit,'mark':minfo}
        
        # add new row with external index start from 1,2,3
        self.symtable.loc[len(self.symtable)+1]=d0
        
    def makeSimuReport(self):
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
        
        # reset tradesup data, because we are running optimization test
        print "set first trade index as set its first tradeidx=",self.bestperfFirstTradeIdx
        self.tradesup.setFirstTradeIdxWithBestPerf(self.bestperfFirstTradeIdx)
        self.tradesup.setTradeReportWithBestPerf(self.bestperfRept)
        
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