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
        self.pattern = '[\d\D]*Zacks Rank : (\d)-[\d\D]*'
        self.path="../data/"
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' "
        print "example:run erdownloadz.py -t aapl"
        print "example:run erdownloadz.py -p portfolio.txt"


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
        for symbol in self.ticklist:
            url = "http://www.zacks.com/stock/quote/"+symbol
            page =urllib2.urlopen(url)
            soup = BeautifulSoup(page.read())
            allitems = soup.findAll('script')
            for index,item in enumerate(allitems):
                txt = item.string
                if txt==None:
                    continue
                '''else:
                    print index,"=",txt'''
                an = re.match(self.earning_exp,txt)
                if an!=None:
                    str1=an.group(1)
                    erlst=[]
                    for pairstr in str1.split(','):
                        name,value = pairstr.split(':')
                        name=re.sub('[{} "]','',name)
                        #print name,value
                        if name=='Date':
                            value=re.sub('[ "]','',value)
                            #d = datetime.datetime.strptime(value, '%m/%d/%Y')
                            erlst.append(value)
                    self.write2File(symbol,erlst)
                    break
                    #print erlst 

    def write2File(self,symbol,erlst):
        fileName=self.path+symbol+"_erdate.erd"
        fp = open(fileName,'w',-1)
        #pickle.dump(erlst, fp)
        #fp.writelines(erlst)
        fp.writelines(["%s\n" % item  for item in erlst])
        fp.close()    


          
    def process(self):
        txt= '<div class="zr_rankbox">\n<p>Zacks Rank : 2-Buy <sup class='
        an = re.match(self.pattern,txt)
        if an!=None:
            str1=an.group(1)
            print str1
        print an
        #self.parseOption()          
        #self.download()
        #self.loadErdFile('msft')
        print "Done,exit..."

################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    erdz = ZackRank()
    erdz.process()
    #process(sys.argv[1:],None)



