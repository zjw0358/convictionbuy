import csv
import pandas
import sys


class SymbolLstStats:
    def __init__(self):
        return
    def process(self):
        self.loadSymbolListCsv(sys.argv[1])
        self.statSector()
        return
    def loadSymbolListCsv(self,fileName):
        # symbol,rank,sector,industry
        fp = open(fileName,'r',-1)
        tickLst=[]
        rankLst=[]
        sectorLst=[]
        industryLst = []
        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue            
            tickLst.append(row[0]) #symbol
            rankLst.append(int(row[1])) #rank
            # skip name
            sectorLst.append(row[3])
            industryLst.append(row[4])
            idx += 1
        fp.close()      # closing
        
        #output
        df = pandas.DataFrame({'symbol':tickLst,'rank':rankLst, \
                'sector':sectorLst,'industry':industryLst},columns=['symbol',\
                'rank','sector','industry'])
        self.symboltable = df[df['rank'] > 0]
                
    def statSector(self):
        # count the sector
        #print self.symboltable.groupby('sector')['sector']
        sectorDct = self.symboltable['sector'].unique()
        #print self.symboltable.groupby(['sector','rank']).count()        
        # rank1 sector
        print "============= rank1 distribution in sector ====================="
        print self.symboltable[self.symboltable['rank']==1].groupby('sector')['sector'].count()        
        return                
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = SymbolLstStats()
    obj.process()        