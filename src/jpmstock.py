import datetime
import sys
import re

class JpmStockFile:
    def __init__(self):


        return
    def procFile(self,fileName):
        fp = open(fileName,'r',-1)

        #print fp
        stocklist = {}
        focuslist = {}
        for line in fp:
            if line=="":
                continue
            #"Apple Inc.",AAPL.O,Yes,"Technology Hardware, Storage &amp; Peripherals" 
            # - >
            #Apple Inc.,AAPL.O,Yes,Technology Hardware, Storage &amp; Peripherals
            #line = re.sub('\"([^"]+)\,([^"]+)\"',r'\1 \2', line)
            line = re.sub('\"([^"]+)\,([^"]+)\"',r'\1 \2', line)
            line = re.sub('[\r\n]','', line)
            # TO CHANGE NEXT TIME
            company,symbolsufx,focus,sector = line.split(',')
            symbol= symbolsufx.split('.')            
            stocklist[symbol[0]] = 1
            if focus=='Yes':
                focuslist[symbol[0]] = 1
        fp.close()
        self.mergeMyPortfolio(stocklist, focuslist)
        
    def mergeMyPortfolio(self, stocklist, focuslist):
        # google style portfolio file
        fp = open(self.mypflfile,'r',-1)
        pf = fp.read()
        #mypfl=[]

        for item in pf.split():            
            market,symbol = item.split(':')
            if not symbol in stocklist:
                print "Add ",symbol
                stocklist[symbol] = 2
                focuslist[symbol] = 2
            else:
                print "Existing ",symbol
                stocklist[symbol] = 3
                focuslist[symbol] = 3                
        fp.close()
        
        self.saveFile(stocklist, focuslist)
        return
        
    def saveFile(self,stocklist, focuslist):
        fileName = self.outputfile + '_' + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        focusfileName = self.outputfile + '_focus_' + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        fp = open(fileName,'w',-1)
        fpfocus = open(focusfileName,'w',-1)
        #fp.writelines(["%s,%s,%s\n" % (company,symbol,sector)  for company,symbol,sector in stocklist])
        #fpfocus.writelines(["%s,%s,%s\n" % (company,symbol,sector)  for company,symbol,sector in focuslist])
        fp.writelines(["%s,%d\n" % (symbol,stocklist[symbol])  for symbol in stocklist])
        fpfocus.writelines(["%s,%d\n" % (symbol,focuslist[symbol])  for symbol in focuslist])

        fp.close()
        fpfocus.close()
        return
        
    def process(self):
        if len(sys.argv)<3:
            print "jpmstock.py inputfile1 myportfolio outputfile"
            sys.exit()
            
        self.outputfile = sys.argv[3]
        self.mypflfile = sys.argv[2]
        self.inputfile = sys.argv[1]
        self.procFile(self.inputfile)
          
if __name__ == "__main__":
    obj = JpmStockFile()
    obj.process()
    #process(sys.argv[1:],None)
