import pandas
import time


class SimuTable:
    def __init__(self, bt):
        self.columns = ['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade','bh_profit','mark'] #,
        self.besttable = pandas.DataFrame(columns=self.columns) 
        self.firstBestResultAdded = False
        self.tradesup = bt.getTradeSupport()
        self.outputpath="../result/"
        self.bestNum = bt.getNumBest()
        self.bestperf = -10000000  # the worse case
        self.bestperfFirstTradeIdx = 0
        self.bestperfRept = pandas.DataFrame()
        self.mode = 1 # optimizer mode, log into simutable
        print "SimuTable initialized"
        return


    def setMode(self, mode):
        self.mode = mode
                
    def setName(self,name):
        self.name = name
         
    #bm=benchmark px 
    def setupSymbol(self,symbol,bm):
        self.symbol=symbol
        self.bm=bm
        self.symtable = pandas.DataFrame(columns=self.columns) 
    
    #param - strategy parameter    
    #df - day value
    #stinfo - setupinfo
    def procStrategyResult(self, stinfo, param, df, minfo=""):
        tradereport = self.tradesup.getTradeReport()
        
        '''
        if self.mode==2: #indicator
            d0={}
            if tradereport.empty:
                d0['lastTrade'] = "empty"
            else:
                d0['lastTrade'] = tradereport.tail(1).to_string(header=False)                
            return d0
        '''    
        bhprofit = self.tradesup.getBHprofit() #buy&hold profit
        perfdata = 0        


        if tradereport.empty:
            lastTrade = "empty"
            # TODO move this to tradesupport?
            d0 = {'symbol':self.symbol,'param':param,'alpha':0,'beta':0,'perf':0,\
            'max_drawdown':0,'profit_order':0,'loss_order':0,'last_trade':lastTrade,'bh_profit':bhprofit,'mark':minfo}
            
            if perfdata>self.bestperf:
                self.bestperf = perfdata
                self.bestdv = df #this is best day value data frame
        else:
            lastTrade = tradereport.tail(1).to_string(header=False)

            firstTradeIdx = self.tradesup.getFirstTradeIdx()
            rtbm = self.bm[firstTradeIdx:].resample('M',how='last')
            bm_returns = rtbm.pct_change()        
            bm_returns = bm_returns.dropna()
            rtsgy = df['dayvalue'][firstTradeIdx:].resample('M',how='last')
            sgy_returns = rtsgy.pct_change()
            sgy_returns=sgy_returns.dropna()
            # get base facts,alpha,beta,volatility,etc
            dct = self.tradesup.getBasefacts(bm_returns,sgy_returns)
            
            #find the best performance
            perfdata = tradereport['pnl'].sum()
            #not printing any more
            #print tradereport,"PnL=",perfdata,"B/H profit=",bhprofit
    
            if perfdata>self.bestperf:
                self.bestperf = perfdata
                self.bestdv = df #this is best day value data frame
                self.bestperfFirstTradeIdx = firstTradeIdx
                self.bestperfRept = self.tradesup.getTradeReport()
                self.bestperfstInfo = stinfo
            
            # TODO move this to tradesupport?
            d0 = {'symbol':self.symbol,'param':param,'alpha':dct['alpha'],'beta':dct['beta'],'perf':perfdata,\
            'max_drawdown':self.tradesup.getMaxdd(),'profit_order':self.tradesup.getProfitOrderNum(),\
            'loss_order':self.tradesup.getLossOrderNum(),'last_trade':lastTrade,'bh_profit':bhprofit,'mark':minfo}
        
        # add new row with external index start from 1,2,3
        self.symtable.loc[len(self.symtable)+1]=d0
        return d0

            
    def procSimuReportnAddBestReport(self, pt = True):
        sortTable = self.symtable.sort_index(by='perf',ascending=False)
        filename = self.outputpath + self.symbol+'_'+self.name+time.strftime('_%Y-%m-%d.csv',time.localtime(time.time()))
        try:
            sortTable.to_csv(filename,sep=',')
        except:
            print "exception when write to csv ",filename
            
        if pt==True:
            print "================================================================"
            print self.symbol + " all simulation results:"
            print sortTable
            print "================================================================"
        
        #add best num result into best report
        bestRows = sortTable[:self.bestNum]
        pieces = [bestRows, self.besttable]
        self.besttable = pandas.concat(pieces)
        # reset tradesup data, because we are running optimization test
        # print "set first trade index as set its first tradeidx=",self.bestperfFirstTradeIdx
        
        if not self.bestperfRept.empty:
            self.tradesup.setFirstTradeIdxWithBestPerf(self.bestperfFirstTradeIdx)
            self.tradesup.setTradeReportWithBestPerf(self.bestperfRept)
            self.tradesup.setStrategyInfoWithBestPerf(self.bestperfstInfo)        
        
    def makeBestReport(self):
        sortTable = self.besttable.sort_index(by='perf')
        filename=self.outputpath+self.name+"_best_"+time.strftime('%Y-%m-%d.csv',time.localtime(time.time()))
        sortTable.to_csv(filename,sep=',',index=False)
        if not sortTable.empty:
            print "================================================================"
            print self.name + " portfolio best performance:"
            print sortTable
            print "================================================================"
            
    def getBestDv(self):
        #print "bestdv=",self.bestdv
        return self.bestdv