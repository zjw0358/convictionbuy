import reuterfunda
import getopt
import sys
import datetime
import marketdata

class merge_reutercsv:
    def __init__(self):
        self.reuter = reuterfunda.ReuterFunda()
        self.mtd = marketdata.MarketData()
        self.oldfile=""
        self.newfile=""
        self.outputfn = "./msdata_reuter_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv' 
        return
        
    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "o:n:h")
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
        for opt, arg in opts:
            if opt in ("-o"):#old reuter file
                self.oldfile = arg
            elif opt in ("-n"):
                self.newfile = arg
            elif opt in ("-h"):
                self.usage()
                sys.exit()   
                
        if self.oldfile=="" or self.newfile=="":
            sys.usage()
            sys.exit()
            
        print "old file=",self.oldfile
        print "new file=",self.newfile
        return
        
    def usage(self):
        print "run merge_reuter.py -o old_reuter.csv -n new_reuter.csv"
        return
    def merge(self):
        olddf = self.reuter.loadReuterCsvFile(self.oldfile)
        newdf = self.reuter.loadReuterCsvFile(self.newfile)
        print "Add these new data:\n",newdf['symbol']
        dfnc = olddf[~olddf['symbol'].isin(newdf['symbol'])]                
        mf = dfnc.append(newdf)
        self.mtd.saveTable(mf,self.outputfn)
        return
    def process(self):
        self.parseOption()
        self.merge()
        print "Done,exit..."
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = merge_reutercsv()
    obj.process()
    