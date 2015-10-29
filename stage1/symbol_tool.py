import marketdata
import getopt
import sys
import datetime
import pandas

class SymbolTool:
    def __init__(self):
        self.mkt = marketdata.MarketData()
        self.basefile = "./marketdata.csv"
        self.portfoliofile = ""
        self.googlefile = ""
        self.option = ""
        self.tickdf = pandas.DataFrame({},columns=['symbol','exg'])
        self.saveToFile = False
        self.pid = 1
        self.outputpath = "./marketdata" + datetime.datetime.now().strftime("_%Y-%m-%d.csv")
        
        return
        
    def usage(self):
        print "=== manipulate portfolio id ==================================="
        print "run symboltool.py -f <base_symbol_list_file> -p <new_portfolio_list> -t <ticklist> -[a/l/c] <pid1,pid2>"
        print "\tc:clear portfolio id"
        print "\ta:add to portfolio id"
        print "\tl:list portfolio id"
        


                
    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:p:g:t:a:c:l:w")
        except getopt.GetoptError:
            print "parse option error"
            self.usage()
            sys.exit() 

        for opt, arg in opts:
            if opt in ("-f"):
                self.basefile = arg
            elif opt in ("-t"):
                self.tickdf = self.mkt.parseTickLstDf(arg)
            elif opt in ("-p"):
                self.portfoliofile = arg
            elif opt in ("-c"):                
                self.option = "clear"
                idLst = arg.split(",")
                self.pid = self.mkt.parsePidLst(idLst)
            elif opt in ("-l"):                
                self.option = "list"
                idLst = arg.split(",")
                self.pid = self.mkt.parsePidLst(idLst)
            elif opt in ("-a"):                
                self.option = "add"
                idLst = arg.split(",")
                self.pid = self.mkt.parsePidLst(idLst)
            elif opt in ("-w"):                
                self.saveToFile = True
        if self.option =="":
            self.usage()
            sys.exit()          
            
    #clear [ticklist] pid 
    def clearPid(self,df,pid):
        if self.tickdf.empty:
            checkSymbol = False
        else:
            checkSymbol = True
            tickdct = self.tickdf.set_index('symbol')['exg'].to_dict()
                    

        for index, row in df.iterrows():
            if checkSymbol:
                if not row['symbol'] in tickdct:
                    continue
            oripid = int(row['pid'])
            newpid = oripid&(~pid)
            df.loc[index,'pid']  = newpid
            print row['symbol'],newpid 
        return df
    
    # assign portfolio with id
    # df - the marketdata.csv(has all symbol data)
    # self.tickdf - to be processed tick
    def addPid(self,df,pid):
        if self.tickdf.empty:
            self.tickdf = self.mkt.loadPortfolioFile(self.portfoliofile)
        #ticklist = self.tickdf['symbol']
        tickdct = self.tickdf.set_index('symbol')['exg'].to_dict()
        
        chgno = 0
        for index, row in df.iterrows():
            if row['symbol'] in tickdct:
                newpid = int(row['pid'])|(pid)
                df.loc[index,'pid']  = newpid
                print row['symbol'],newpid
                chgno+=1
        print "total symbollist number=",len(df.index)
        print "changed number=",chgno
        return df
    
    
                
        
    def process(self): 
        self.parseOption()
        df = self.mkt.loadSymbolLstFile(self.basefile)
        #print self.basefile
        #print self.pid
        
        if self.option=="list":
            df1 = self.mkt.getSymbolByPid(df,self.pid)
            if not self.tickdf.empty:
                df1 = df1[df1['symbol'].isin(self.tickdf['symbol'])]
            '''
            print "====="
            who use this?
            lst = df1['symbol'].values.tolist()
            for x in lst:
                print x
            '''
            print df1,"\nnumber=",len(df1.index)
        elif self.option=="clear":
            df1 = self.clearPid(df,self.pid)
        elif self.option=="add":
            df1 = self.addPid(df,self.pid)

            
        if self.option=="add" or self.option=="clear":
            self.mkt.saveTable(df1,self.outputpath)
        elif self.saveToFile:
            self.mkt.saveTable(df1,self.outputpath)
        return
           
if __name__ == "__main__":
    obj = SymbolTool()
    obj.process()
'''
    def addPid0(self,df,pid):
        if len(self.ticklist)==0:
            self.ticklist = self.mkt.loadPortfolioFile(self.portfoliofile)
            
        for index, row in df.iterrows():
            if row['symbol'] in self.ticklist:
                newpid = int(row['pid'])|(pid)
                df.loc[index,'pid']  = newpid
                print row['symbol'],newpid
        print "number=",len(df.index)
        return df
'''        