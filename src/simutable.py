import pandas
import time


class SimuTable:
    def __init__(self,support):
        columns = ['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade'] #,
        self.besttable = pandas.DataFrame(columns=columns) 
        self.firstBestResultAdded = False
        self.support = support
        print "SimuTable initialized"

        return
    def setName(self,name):
        self.name = name
          
    def setupSymbol(self,symbol,bm):
        self.symbol=symbol
        self.bm=bm
        columns = ['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade'] #,
        #dftbl = pandas.DataFrame(columns=columns,index=length) 
        self.symtable = pandas.DataFrame(columns=columns) 
    
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
        
        # get base facts,alpha,beta,volatility,etc
        dct = self.support.basefacts(bm_returns,sgy_returns)
        

        tradereport = self.support.getTradeReport()
        lastTrade = tradereport.tail(1).to_string(header=False)
        
        perfdata = tradereport['pnl'].sum()
        #param = "k1=%.1f,k2=%.1f,cf=%d"%(k1,k2,cl)
        
        d0 = {'symbol':self.symbol,'param':param,'alpha':dct['alpha'],'beta':dct['beta'],'perf':perfdata,\
        'max_drawdown':self.support.getMaxdd(),'profit_order':self.support.getProfitOrderNum(),\
        'loss_order':self.support.getLossOrderNum(),'last_trade':lastTrade}
        
        # add new row with external index start from 1,2,3
        self.symtable.loc[len(self.symtable)+1]=d0
        
    def makeSymbolReport(self):
        sortTable = self.symtable.sort_index(by='perf')
        filename=self.symbol+'_'+self.name+time.strftime('_%Y-%m-%d.csv',time.localtime(time.time()))
        sortTable.to_csv(filename,sep=',')
        
        print "================================================================"
        print self.symbol + " all simulation results:"
        print sortTable
        print "================================================================"
        
        # add best result to best table,index = 1
        #print sortTable.tail(1)
        bestrow = sortTable.tail(1).iloc[0]
        #bestrow['symbol']=self.symbol
        #print bestrow,type(bestrow)
        #if self.firstBestResultAdded==True:
        #    print self.besttable
        
        '''if self.firstBestResultAdded==False:
            self.besttable = bestrow
            self.firstBestResultAdded = True
        else:
            self.besttable.loc[len(self.besttable)+1]=bestrow'''
        self.besttable.loc[len(self.besttable)+1]=bestrow
        
        #bestrow = bestrow[['symbol','param','alpha', 'beta','perf','max_drawdown','profit_order','loss_order','last_trade']]
        #print bestrow,type(bestrow)
        #print self.besttable.add(bestrow,fill_value="")
        #self.besttable.loc[len(self.besttable)+1]=bestrow
        #print self.besttable
         
        '''print dftbl
        idx = dftbl['perf'].argmax()
        drow = dftbl.loc[idx]
        drow['symbol']='aapl'
        print drow
        dftbl.to_excel(writer,'Sheet1')
        writer.save()''' 
        
    def makeBestReport(self):
        sortTable = self.besttable.sort_index(by='perf')
        filename=self.name+"_best_"+time.strftime('%Y-%m-%d.csv',time.localtime(time.time()))
        sortTable.to_csv(filename,sep=',')
        print "================================================================"
        print self.name + " portfolio best performance:"
        print sortTable
        print "================================================================"
            
        