import getopt
import datetime
import sys
import csv
import pandas

'''
load market data

'''
class MarketData:
    def __init__(self):
        #pandas.set_option('display.max_columns', 50)
        #pandas.set_option('display.precision', 3)
        #pandas.set_option('display.expand_frame_repr', False)
        
        #self.columns = ['symbol','5d','10d','20d', '50d', '100d','200d','max','px', \
        #                'sma10','sma50','sma200','sma10%','sma50%','sma200%']
        #self.perftable = pandas.DataFrame(columns=self.columns) 
        #self.outputpath = "../result/"        
        
        #pandas.options.display.float_format = '{:,.2f}%'.format
        #self.spdretf = {'Consumer Discretionary':'XLY','Consumer Staples':'XLP','Energy':'XLE',\
        #            'Financials':'XLF','Health Care':'XLV','Industrials':'XLI','Materials':'XLB',\
        #            'Technology':'XLK','Utilities':'XLU'}
        #TODO            
        #self.sectormapping = {'Consumer Discretionary':'Consumer Services','Consumer Staples':'Consumer Non-Durables',\
        #        'Energy':'Energy','Financials':'Finance','Health Care':'Health Care','Technology':'Technology',\
        #        'Industrials':'Basic Industries','Industrials':'Transportation','Industrials':'Capital Goods',\
        #        'Materials':'Basic Industries','Capital Goods':'xlb','Health Care':'xlv','Consumer Services':'xly', \
        #        'Utilities':'Public Utilities'}              
       
        return
        
        
    def loadSymbolLstFile(self,fileName):
        #symbol,rank,name,sector,industry,pid,exg
        fp = open(fileName,'r',-1)
        symbolLst = []
        rankLst = []
        nameLst = []
        sectorLst = []
        industryLst = []
        pidLst = []
        exgLst = []
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        try:
            for row in reader:
                if idx==0:
                    idx += 1
                    continue
                symbolLst.append(row[0])
                rankLst.append(int(row[1]))
                nameLst.append(row[2])
                sectorLst.append(row[3])
                industryLst.append(row[4])
                pidLst.append(row[5])
                exgLst.append(row[6])
                idx += 1
        except:
            print "error when reading symbol list file, exit..."
            sys.exit()
        fp.close()      # closing
        table = pandas.DataFrame({'symbol':symbolLst,'rank':rankLst,'name':nameLst,\
            'sector':sectorLst,'industry':industryLst,'pid':pidLst,'exg':exgLst},\
            columns=['symbol','rank','name','sector','industry','pid','exg'])
        return table

   
  