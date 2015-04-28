import marketdata
import getopt
import sys
import datetime

class SymbolTool:
    def __init__(self):
        self.mkt = marketdata.MarketData()
        self.basefile = "./marketdata.csv"
        self.portfoliofile = ""
        self.googlefile = ""
        self.option = ""
        self.ticklist = {}
        self.pid = 1
        self.outputpath = "./marketdata" + datetime.datetime.now().strftime("_%Y-%m-%d.csv")
        
        return
        
    def usage(self):
        print "=== manipulate portfolio id ==================================="
        print "run symboltool.py -f <base_symbol_list_file> -p <new_portfolio_list> -t <ticklist> -[a/l/c] <pid1,pid2>"


                
    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:p:g:t:a:c:l:")
        except getopt.GetoptError:
            print "parse option error"
            self.usage()
            sys.exit() 

        for opt, arg in opts:
            if opt in ("-f"):
                self.basefile = arg
            elif opt in ("-t"):
                newstr = arg #.replace("", "")                
                lst = newstr.split(",")
                for sym in lst:
                    self.ticklist[sym]=""
            elif opt in ("-p"):
                self.portfoliofile = arg
            #elif opt in ("-i"):
            #    idLst = arg.split(",")
            #    self.pid = self.mkt.parsePidLst(idLst)
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
                   
        if self.option =="":
            self.usage()
            sys.exit()  
        
    
    '''                 
    def getNewPflId(self,maxid):
        num = 0
        while (maxid>0):
            maxid = (maxid>>1)
            num += 1
        return 2**num

    def merge(self):
        df1 = self.mkt.loadSymbolLstFile(self.file1)
        df2 = self.mkt.loadSymbolLstFile(self.file2)
        df2dct = dict(zip(df2.symbol,df2.sector))        
        for index, row in df1.iterrows():            
            #print row['symbol'],(row['symbol'] in df2['symbol'])
            if row['symbol'] in df2dct:
                df1.loc[index,'pid'] = int(row['pid'])|self.newid
                #print row['symbol'],df1.loc[index,'pid']
        return df1
        
    def delpid(self):
        df1 = self.mkt.loadSymbolLstFile(self.file1)
        for index, row in df1.iterrows(): 
            pid = int(row['pid'])            
            if (pid&self.newid)==1:
                df1.loc[index,'pid'] = int(row['pid'])|(~self.newid)
        return df1
    '''
    def clearPid(self,df,pid):
        for index, row in df.iterrows():
            oripid = int(row['pid'])
            df.loc[index,'pid']  = oripid&(~pid)
        return df
    
    # assign portfolio with id
    def addPid(self,df,pid):
        if len(self.ticklist)==0:
            self.ticklist = self.mkt.loadPortfolioFile(self.portfoliofile)
            
        for index, row in df.iterrows():
            if row['symbol'] in self.ticklist:
                newpid = int(row['pid'])|(pid)
                df.loc[index,'pid']  = newpid
                print row['symbol'],newpid
        print "number=",len(df.index)
        return df
        
        
    def process(self): 
        self.parseOption()
        df = self.mkt.loadSymbolLstFile(self.basefile)
        #print self.basefile
        #print self.pid
        
        if self.option=="list":
            df1 = self.mkt.getSymbolByPid(df,self.pid)
            print df1,"\nnumber=",len(df1.index)
            print "====="
            #print type(df1['symbol'])
            lst = df1['symbol'].values.tolist()
            for x in lst:
                print x
            #print(df1['symbol'].to_csv(sep='\t', index=False))
            #print lst
        elif self.option=="clear":
            df1 = self.clearPid(df,self.pid)
        elif self.option=="add":
            df1 = self.addPid(df,self.pid)

        
        if self.option=="add" or self.option=="clear":
            self.mkt.saveTable(df1,self.outputpath)
        
        return
           
if __name__ == "__main__":
    obj = SymbolTool()
    obj.process()
        