import csv
import datetime
import zackrank
import sys

class UpdateZackRank:
    def __init__(self):
        self.outputpath = "../data/"
        self.zack = zackrank.ZackRank()
        
    def loadMergeCsv(self,fileName):
        # symbol,rank,sector,industry
        fp = open(fileName,'r',-1)
        #print fp
        outputfn = self.outputpath + "zrupdate_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        outputfp = open(outputfn,'w',-1)
         
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            symbol = row[0]
            rank = row[1]
            #self.stocklist[symbol] = row
            #print symbol
            if '^' in symbol or rank=="-1":
                continue
            if rank == "":
                ret = self.zack.getSymbolRank(symbol)
                row[1] = str(ret)
            line = "%s,%s,%s,%s,%s\n" % (row[0],row[1],row[2],row[3],row[4])
            print idx,line
            idx += 1
            outputfp.write(line)
            if idx%10 == 0:
                outputfp.flush()
        fp.close()      # closing
        outputfp.close()
        return
        
if __name__ == "__main__":
    obj = UpdateZackRank()
    obj.loadMergeCsv(sys.argv[1])
        