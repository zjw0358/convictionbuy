#http://www.nasdaq.com/screening/company-list.aspx
# process nasdaq company list
import datetime
import csv
import zackrank

class CompanyList:
    def __init__(self):
        self.nasdaqcsv = "../data/nasdaq.csv"
        self.nysecsv = "../data/nyse.csv"
        self.amexcsv = "../data/amex.csv"
        self.stocklist = {} #hashtable
        self.outputpath = "../data/"
        self.zack = zackrank.ZackRank()
    '''
    Symbol  : ZUMZ
    Name    : Zumiez Inc.
    LastSale: 37.93
    MarketCap: 1108464651.08
    ADR TSO : n/a
    IPOyear : 2005
    Sector  : Consumer Services
    industry: Clothing/Shoe/Accessory Stores
    Summary Quote: http://www.nasdaq.com/symbol/zumz

    '''    
    def loadCompFile(self,filename):
        f = open(filename, 'r', -1)
        reader = csv.reader(f)  # creates the reader object
        rownum = 0
        for row in reader:
            if rownum == 0:
                self.header = row
            else:
                '''colnum = 0
                for col in row:
                    print '%-8s: %s' % (header[colnum], col)
                    colnum += 1
                '''
                
                row[0] = row[0].replace(" ","")
                row[1] = row[1].replace(",","")
                row[6] = row[6].replace(",","")
                row[7] = row[7].replace(",","")
                symbol = row[0]
                #print type(row)
                row.append("") #rank
                self.stocklist[symbol] = row
            rownum += 1
       
        f.close()      # closing
   

    def mergeZack(self):
        # common style symbol list
        fileName= "../data/zackrank_2015-01-17.csv"
        fp = open(fileName,'r',-1)
        
        reader = csv.reader(fp)  # creates the reader object
        rownum = 0
        for row in reader:
            symbol = row[0]
            rank = row[1]
            if symbol in self.stocklist:
                data = self.stocklist[symbol]
                data[-1] = rank
        fp.close()      # closing
        return
        
    # symbol
    def loadDow30Lst(self,fileName):
        self.dow30Lst = {}
        self.dow30id = 1
        fp = open(fileName,'r',-1)        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            if row[0]!="":
                self.dow30Lst[row[0]] = row[0]
            idx += 1
        fp.close()      # closing
        return self.dow30Lst

    # google style portfolio file, NYSE:DOW NASDAQ:GOOG
    def loadGoogFocusLst(self,fileName):        
        fp = open(fileName,'r',-1)
        pf = fp.read()
        self.foucsLst = {}
        self.focusid = 2        

        for item in pf.split():            
            market,symbol = item.split(':')
            self.foucsLst[symbol] = symbol
        fp.close()
        return self.foucsLst

    # all symbols list with zack rank
    def loadAllSymbolLst(self,fileName):
        # symbol,rank,name,sector,industry,portfolio_id
        fp = open(fileName,'r',-1)
        self.allsymbol = {}         
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx +=1
                continue            
            symbol = row[0]
            # temp
            row.append(0)
            # temp
            self.allsymbol[symbol] = row
            idx += 1
        fp.close()      # closing
        return self.allsymbol
           
    '''
    def saveStockList(self):
        fileName = self.outputpath + "allstock_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        fp = open(fileName,'w',-1)
        
        for symbol in self.stocklist:
            data = self.stocklist[symbol]
            str = "%s,%s,%s,%s,%s\n" % (symbol,data[-1],data[1],data[6],data[7])
            #symbol,rank,name,sector,industry
            fp.write(str)
        fp.close()
    ''' 
    # merge dow30,focus and allsymbol into one (with portfolio id)
    def mergeAllFiles(self):
        self.loadDow30Lst("../data/dow30.txt")
        self.loadGoogFocusLst("../data/googfocuslist.txt")
        self.loadAllSymbolLst("../data/allsymbolhaverank.csv")
        for symbol in self.dow30Lst:
            if not symbol in self.allsymbol:
                #symbol,rank,name,sector,industry,portfolio_id
                row = [symbol,"-2","","",""]
                self.allsymbol[symbol] = row
                print "Add DOW30",symbol
        #merge
        for symbol in self.dow30Lst:
            if not symbol in self.allsymbol:
                #symbol,rank,name,sector,industry
                row = [symbol,"-2","","","",0]
                self.allsymbol[symbol] = row
                print "Add DOW30",symbol
                
        for symbol in self.foucsLst:
            if not symbol in self.allsymbol:
                #symbol,rank,name,sector,industry
                row = [symbol,"-2",symbol,symbol,symbol,0]
                self.allsymbol[symbol] = row
                print "Add Focus",symbol
        # update portfolio id and write to file
        outputfn = self.outputpath + "allsymbollist_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        outputfp = open(outputfn,'w',-1)
        outputfp.write("symbol,rank,name,sector,industry,pid")
        for symbol in self.allsymbol:
            row = self.allsymbol[symbol]
            if symbol in self.dow30Lst:
                row[-1] = row[-1]|self.dow30id
            if symbol in self.foucsLst:
                row[-1] = row[-1]|self.focusid
            line = "%s,%s,%s,%s,%s,%d\n" % (row[0],row[1],row[2],row[3],row[4],row[5])   
            outputfp.write(line)
        outputfp.close()
         
    def process(self):
        '''
        self.loadCompFile(self.nasdaqcsv)
        self.loadCompFile(self.nysecsv)
        self.loadCompFile(self.amexcsv)
        self.mergeZack()
        self.saveStockList()
        '''
        self.mergeAllFiles()
        print "Done,Exit..."
        
        
if __name__ == "__main__":
    obj = CompanyList()
    obj.process()
        