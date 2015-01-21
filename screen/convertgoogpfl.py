import datetime
import getopt
import sys

class ConvertGoogPortfolio:
    def __init__(self):
        self.outputfn = ""
        self.inputfn = ""
        return
        
    # google style portfolio file
    def loadPortfolioFile(self,fileName):
        #print "open file:",fileName
        fp = open(fileName,'r',-1)
        pf = fp.read()
        stocklist=[]
        #print pf
        for item in pf.split():            
            market,symbol = item.split(':')
            print symbol
            stocklist.append(symbol)
                    
        fp.close()
        return stocklist
        
    def usage(self):
        print "program -i input -o output"
        print "convert google style portfolio to symbol list csv"
               
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["input", "output"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-i", "--input"):
                self.inputfn = arg
            elif  opt in ("-o", "--output"):
                self.outputfn = arg
            
        if (self.inputfn=="" or self.outputfn==""):
            self.usage()
            sys.exit()
        return

    def process(self):
        self.parseOption()
        stocklist = self.loadPortfolioFile(self.inputfn)
        self.saveSymbolList(stocklist)
        
    def saveSymbolList(self,stocklist):        
        outputfp = open(self.outputfn,'w',-1)
        for symbol in stocklist:
            outputfp.write(symbol)
            outputfp.write('\n')
        outputfp.close()
        return
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ConvertGoogPortfolio()
    obj.process()