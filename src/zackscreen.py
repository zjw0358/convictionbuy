import zackrank
import sys
import getopt
import datetime

class ZackScreen:
    def __init__(self):
        self.zack = zackrank.ZackRank()
        self.outputpath="../result/"
        columns = ['symbol','rank','cq','cq7','cq30','cq60', 'cq90', 'abr','abr1w','abr1m','abr2m', \
                        'abr3m']
        return
    def usage(self):
        print "program -f portfolio"
        
    def process(self):
        self.parseOption()
        #self.getZackRank()
        self.getPriceSale()
        return
        
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:", ["filename", "ticklist"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.ticklist = self.loadSymbolLstFile(arg)
            elif opt in ("-t", "--ticklist"):
                newstr = arg.replace("'", "")                
                self.ticklist = newstr.split()
                
        if (not self.ticklist):
            self.usage()
            sys.exit()
        return
           
    # common style symbol list
    # symbol, source(1/2/3), 1-JPM,2-my portfolio,3-both
    def loadSymbolLstFile(self,fileName):
        fp = open(fileName,'r',-1)
        stocklist = []
        for line in fp:            
            items = line.split(',')
            stocklist.append(items[0])
        fp.close()
        return stocklist
        
    # google style portfolio file
    def loadPortfolioFile(self,fileName):     
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
    
    # yahoo
    def getPriceSale(self):       
        stockps = self.zack.getPriceSale(self.ticklist)
        
        
        
    def getZackRank(self):
        rankdict = self.zack.getRank(self.ticklist)
        if len(rankdict) > 1:
            fileName = self.outputpath + "zackrank_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
            fp = open(fileName,'w',-1)
            fp.writelines(["%s,%d\n" % (item, rankdict[item])  for item in rankdict])
            fp.close()
        else:
            print rankdict
        return rankdict
    
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    zs = ZackScreen()
    zs.process()
