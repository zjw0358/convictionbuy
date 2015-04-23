import marketdata
import getopt
import sys
import datetime

class SymbolTool:
    def __init__(self):
        self.mkt = marketdata.MarketData()
        self.basefile = "./marketdata.csv"
        self.portfoliofile = ""
        self.option = ""
        self.ticklist = []
        self.pid = 1
        self.outputpath = "./marketdata_" + datetime.datetime.now().strftime("_%Y-%m-%d.csv")
        
        return
        
    def usage(self):
        print "run symboltool.py -f <base_symbol_list_file> -p <new_portfolio_list> -t <ticklist> -[l/c] "
        print "=== manipulate portfolio id ==================================="

                
    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:i:t:i:cl")
        except getopt.GetoptError:
            print "parse option error"
            return False

        for opt, arg in opts:
            if opt in ("-f"):
                self.basefile = arg
            elif opt in ("-t"):
                newstr = arg #.replace("", "")                
                self.ticklist = newstr.split(",")
            elif opt in ("-p"):
                self.portfoliofile = arg
            elif opt in ("-i"):
                idLst = arg.split(",")
                self.pid = self.mkt.parsePidLst(idLst)
            elif opt in ("-c"):                
                self.option = "clear"
            elif opt in ("-l"):                
                self.option = "list"            
        #if self.option =="" or self.newid==-1:
        #    self.usage()
        #    sys.exit()  
        
    
                 
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

    def clearPid(self,df,pid):
        for index, row in df.iterrows():
            oripid = int(row['pid'])
            df.loc[index,'pid']  = oripid&(~pid)
            #print row['symbol'],row['pid']
        return df
                  
    def process(self): 
        self.parseOption()
        df = self.mkt.loadSymbolLstFile(self.basefile)

        print ~self.pid
        
        if self.option=="list":
            df1 = self.mkt.getSymbolByPid(df,self.pid)
        elif self.option=="clear":
            df1 = self.clearPid(df,self.pid)
        else:
            return
            
        print df1
        
        try:
            df1.to_csv(self.outputpath,sep=',',index=False)
        except:
            print "exception when write to csv ",self.outputpath
            
        print "Finish wrote to ",self.outputpath
        
        return
           
if __name__ == "__main__":
    obj = SymbolTool()
    obj.process()
        