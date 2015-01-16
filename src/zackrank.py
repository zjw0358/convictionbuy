#from bs4 import BeautifulSoup
import urllib2
import re
import datetime
import sys
import getopt

from bs4 import BeautifulSoup



class ZackRank:
    def __init__(self):
        #self.earning_exp = '^window.app_data_earnings[\d\D]*\\"data\\"[ :\\[]*(.*)]'
        self.rankPattern = '[\d\D]*Zacks Rank : (.*) <sup class=[\d\D]*'
        self.outputpath="../result/"
        columns = ['symbol','rank','cq','cq7','cq30','cq60', 'cq90', 'abr','abr1w','abr1m','abr2m', \
                        'abr3m']

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
    
    # common style symbol list
    # symbol, source(1/2/3),
    def loadSymbolLstFile(self,fileName):
        fp = open(fileName,'r',-1)
        stocklist = []
        for line in fp:            
            items = line.split(',')
            stocklist.append(items[0])
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
        
    def getRank(self):
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
    '''
    Brokerage Recommendations

    Today	1 Week Ago	1 Month Ago	2 Months Ago	3 Months Ago
    Strong Buy	22	22	22	22	22
    Buy	4	4	4	4	5
    Hold	6	6	6	6	6
    Sell	0	0	0	0	0
    Strong Sell	0	0	0	0	0
    ABR	1.50	1.50	1.50	1.50	1.52
    '''        
    def getBrokerRecom(self):
        url = "http://www.zacks.com/stock/research/NOC/brokerage-recommendations"
    '''
    Magnitude - Consensus Estimate Trend

    Current Qtr     (12/2014)	Next Qtr     (3/2015)	Current Year     (12/2014)	Next Year(12/2015)
    Current	0.66	0.51	2.25	2.40
    7 Days Ago	0.66	0.51	2.25	2.40
    30 Days Ago	0.66	0.51	2.25	2.40
    60 Days Ago	0.66	0.52	2.25	2.38
    90 Days Ago	0.66	0.52	2.24	2.39
    '''
    def getEstimate(self, symbol):
        url = "http://www.zacks.com/stock/quote/" + symbol + "/detailed-estimates"
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        print page
        allitems = soup.findAll("section") #,id='magnitude_estimate'
        for index,item in enumerate(allitems):
            txt = item.string
            if txt==None:
                continue
            print txt
            
        
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
        self.getRank()
        print "Done,exit..."

################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    zr = ZackRank()
    zr.getEstimate('msft')
    #process(sys.argv[1:],None)



