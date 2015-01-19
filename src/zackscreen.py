#import zackrank
import sys
import getopt
import datetime
import fundata
import csv
import pandas

class ZackScreen:
    def __init__(self):
        #self.zack = zackrank.ZackRank()
        self.funda = fundata.FundaData()
        self.outputpath="../result/"
        self.symtable=pandas.DataFrame()
        #columns = ['symbol','rank','cq','cq7','cq30','cq60', 'cq90', 'abr','abr1w','abr1m','abr2m', \
        #                'abr3m']
        return
    def usage(self):
        print "program -f portfolio.txt"
        
    def process(self):
        self.parseOption()
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
                self.loadSymbolLstFile(arg)
                
        if (self.symtable.empty):
            self.usage()
            sys.exit()
        return
           
    # ABR update file
    # symbol,rank,indurank,indutotal,etf,abrt,abr1w,abr1m,abr2m,abr3m,numbr
    def loadSymbolLstFile(self,fileName):
        fp = open(fileName,'r',-1)
        header=[]
        #header = 'symbol,rank,indurank,indutotal,etf,abrt,abr1w,abr1m,abr2m,abr3m,numbr\n'
        reader = csv.reader(fp)  # creates the reader object
        symbolLst=[]
        rankLst=[]
        indurankLst=[]
        indutotalLst=[]
        eftLst=[]
        abrtLst=[]
        abr1wLst=[]
        abr1mLst=[]
        abr2mLst=[]
        abr3mLst=[]
        numbrLst=[]

        idx = 0
        for row in reader:
            if idx == 0:
                header = row
            else:
                symbolLst.append(row[0])
                rankLst.append(int(row[1]))
                indurankLst.append(row[2])
                indutotalLst.append(row[3])
                eftLst.append(row[4])
                #print row[0],row[5]
                if row[5]=="" or row[5]=="NA":
                    abrtLst.append(0)
                else:
                    abrtLst.append(float(row[5]))
                abr1wLst.append(row[6])
                abr1mLst.append(row[7])
                abr2mLst.append(row[8])
                abr3mLst.append(row[9])
                numbrLst.append(row[10])
            idx += 1            
        fp.close() 
        #load into pandas data frame
        self.symtable=pandas.DataFrame({'symbol':symbolLst,'rank':rankLst,\
            'industry_rank':indurankLst,'industry_total':indutotalLst,'etf':eftLst,\
            'abr_today':abrtLst,'abr_1week':abr1wLst,'abr_1month':abr1mLst,\
            'abr_2month':abr2mLst,'abr_3month':abr3mLst,'num_of_br':numbrLst},\
            columns=['symbol','rank','industry_rank','industry_total','etf','abr_today',\
            'abr_1week','abr_1month','abr_2month','abr_3month'])
        #
        return
        
   
    
    # yahoo
    def getPriceSale(self): 
        ticklist = self.symtable[(self.symtable['rank']<=3) & (self.symtable['rank']>0) & \
            (self.symtable['abr_today'] < 2) & (self.symtable['abr_today'] > 0)]
        #& self.symtable['rank']>0 & self.symtable['abr_today']<2
        print ticklist
        print len(ticklist)
        #self.funda.getPriceSale(ticklist)

        
        
        
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
