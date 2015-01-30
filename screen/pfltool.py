import marketdata
import getopt
import sys
import datetime

class PortfolioTool:
    def __init__(self):
        self.mkt = marketdata.MarketData()
        self.file1 = ""
        self.file2 = ""
        self.option = ""
        self.newid = -1
        self.outputpath = "../result/newpfl" + datetime.datetime.now().strftime("_%Y-%m-%d.csv")
        return
        
    def usage(self):
        print "program -f <old_portfolio_file> -t <new_portfolio_file> -[a/d] "
        print "=== manipulate portfolio id ==================================="

                
    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "a:b:i:c:", ["filename", "newpfl", "id","action"])
        except getopt.GetoptError:
            print "parse option error"
            return False

        for opt, arg in opts:
            if opt in ("-a", "--file1"):
                self.file1 = arg
            elif opt in ("-b", "--file2"):
                self.file2 = arg
            elif opt in ("-i", "--id"):                
                newid = int(arg)
                if newid<=2:
                    print "Not allowed to use pid <=2, change to 3"
                    newid = 3                    
                self.newid = 2**(newid-1)
            elif opt in ("-c", "--action"):                
                self.option = arg        
                        
        if self.option =="" or self.newid==-1:
            self.usage()
            sys.exit()  
            
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

                
    def process(self): 
        self.parseOption()
        # save to new file
        if self.option=="add":
            df1 = self.merge()
        elif self.option=="del":
            df1 = self.delpid()
        else:
            return
        try:
            df1.to_csv(self.outputpath,sep=',',index=False)
        except:
            print "exception when write to csv ",self.outputpath
            
        print "Finish wrote to ",self.outputpath
        return
           
if __name__ == "__main__":
    obj = PortfolioTool()
    obj.process()
        