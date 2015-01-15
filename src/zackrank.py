#from bs4 import BeautifulSoup
import urllib2
import re
import datetime
import sys
import getopt
#import pickle

class ZackRank:
    def __init__(self):
        #self.earning_exp = '^window.app_data_earnings[\d\D]*\\"data\\"[ :\\[]*(.*)]'
        self.pattern = '[\d\D]*Zacks Rank : (.*) <sup class=[\d\D]*'
        self.outputpath="../result/"
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' "
        print "example:run zackrank.py -t aapl"
        print "example:run zackrank.py -p portfolio.txt"

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
        
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:", ["filename", "ticklist"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.ticklist = self.loadPortfolioFile(arg)
            elif opt in ("-t", "--ticklist"):
                newstr = arg.replace("'", "")                
                self.ticklist = newstr.split()
                
        if (not self.ticklist):
            self.usage()
            sys.exit()
        return
        
    def download(self):
        zackranks = {}
        for symbol in self.ticklist:
            url = "http://www.zacks.com/stock/quote/"+symbol
            htmltxt =urllib2.urlopen(url).read()
            an = re.match(self.pattern, htmltxt)
            if an!=None:
                str1=an.group(1)
                if str1=='NA':
                    zrank = 0
                else:
                    zrank = int(str1[0])
                print symbol, zrank
                zackranks[symbol] = zrank

        if len(zackranks) > 1:
            self.write2File(zackranks)
            
    def getBrokerRecom(self):
        url = "http://www.zacks.com/stock/research/NOC/brokerage-recommendations"
        
        
    def write2File(self,zackranks):
        fileName=self.outputpath + "zackrank_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        fp = open(fileName,'w',-1)
        fp.writelines(["%s,%d\n" % (item,zackranks[item])  for item in zackranks])
        fp.close()

    def test(self):
        #txt= '<div class="zr_rankbox">\n<p>Zacks Rank : 2-Buy <sup class=xxx\nmmk\n'
        txt = 'Zacks Rank : NA <sup class=xxx\nmmk'
        an = re.match(self.pattern,txt)
        if an!=None:
            str1=an.group(1)
            print str1
        print an
          
    def process(self):
        self.parseOption()          
        self.download()
        print "Done,exit..."

################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    erdz = ZackRank()
    erdz.process()
    #process(sys.argv[1:],None)



