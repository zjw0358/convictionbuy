import pandas
import time


class TestReport:
    def __init__(self,bt):
        self.columns = ['symbol','strategy','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade','bh_profit'] #,
        self.besttable = pandas.DataFrame(columns=self.columns) 
        self.firstBestResultAdded = False
        self.tradesup = bt.getTradeSupport()
        self.outputpath = bt.getResultPath()
        self.bestperf = 0
        self.bestperfFirstTradeIdx = 0
        self.reptName = "batchtest"
        #self.bestdv# = pandas.DataFrame(columns='dayvalue')
        print "TestReport initialized"

        return
         
    #bm=benchmark px 
    def setup(self,bm):
        self.bm = bm
        self.reptTable = pandas.DataFrame(columns=self.columns) 
    
    #param - strategy parameter    
    #df - day value
    def addTestResult(self,symbol,stgyName,param,df):
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
        lastTrade = tradereport.tail(1).to_string(header=False)
        
        #find the best performance
        perfdata = tradereport['pnl'].sum()
        print tradereport,"PnL=",perfdata,"B/H profit=",bhprofit
        if perfdata>self.bestperf:
            self.bestperf = perfdata
            self.bestdv = df #this is best day value data frame
            self.bestperfFirstTradeIdx = firstTradeIdx
            
        
        d0 = {'symbol':symbol,'strategy':stgyName,'param':param,'alpha':dct['alpha'],'beta':dct['beta'],'perf':perfdata,\
        'max_drawdown':self.tradesup.getMaxdd(),'profit_order':self.tradesup.getProfitOrderNum(),\
        'loss_order':self.tradesup.getLossOrderNum(),'last_trade':lastTrade,'bh_profit':bhprofit}
        
        # add new row with external index start from 1,2,3
        self.reptTable.loc[len(self.reptTable)+1]=d0
        
    def createTestReport(self):
        sortTable = self.reptTable.sort_index(by='perf',ascending=False)
        filename = self.outputpath + self.reptName+'_' + time.strftime('_%Y-%m-%d.csv',time.localtime(time.time()))
        try:
            sortTable.to_csv(filename,sep=',')
        except:
            print "exception when write to csv ",filename
        
        print "================================================================"
        print "BATCH TEST RESULT:"
        print sortTable
        print "================================================================"
        

        #bestrow = sortTable.head(1).iloc[0]        
        #self.besttable.loc[len(self.besttable)+1]=bestrow
        
        #
        #print "set first trade index as set its first tradeidx=",self.bestperfFirstTradeIdx
        #self.tradesup.setFirstTradeIdxWithBestPerf(self.bestperfFirstTradeIdx)
        
    
            
    def getBestDv(self):
        #print "bestdv=",self.bestdv
        return self.bestdv