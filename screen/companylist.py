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
        
    def loadAllSymbolLst(self,fileName):
        # symbol,rank,name,sector,industry,portfolio_id
        fp = open(fileName,'r',-1)
        #print fp
        outputfn = self.outputpath + "allsymbollst_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        outputfp = open(outputfn,'w',-1)
         
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            symbol = row[0]
            pid = 0
            if symbol in self.dow30Lst:
                pid = pid|self.dow30id
            if symbol in self.focusLst:
                pid = pid|self.focusid
                
            line = "%s,%s,%s,%s,%s\n" % (row[0],row[1],row[2],row[3],row[4])
            print idx,line
            idx += 1
            outputfp.write(line)
            if idx%10 == 0:
                outputfp.flush()
        fp.close()      # closing
        outputfp.close()
        return
           
    def saveStockList(self):
        fileName = self.outputpath + "allstock_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        fp = open(fileName,'w',-1)
        
        for symbol in self.stocklist:
            data = self.stocklist[symbol]
            str = "%s,%s,%s,%s,%s\n" % (symbol,data[-1],data[1],data[6],data[7])
            #symbol,rank,name,sector,industry
            fp.write(str)
        fp.close()
        
        
    def addNewCol(self):
        dow30Lst = {}
        self.loadSymbolLstFile(dow30Lst)
        
    def process(self):
        '''
        self.loadCompFile(self.nasdaqcsv)
        self.loadCompFile(self.nysecsv)
        self.loadCompFile(self.amexcsv)
        self.mergeZack()
        self.saveStockList()
        '''

        
        
if __name__ == "__main__":
    obj = CompanyList()
    obj.process()
        