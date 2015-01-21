import csv
import datetime
import zackrank
import sys
import getopt

'''
used to update zack ABR periodly
updatezackabr.py ../data/zrupdate_2015-01-18.csv 
output - ../data/zrupdate_[time].csv
'''
#TODO check ETF
class UpdateZackAbr:
    def __init__(self):
        self.outputpath = "../data/"
        self.abrname = "zrabr_"
        self.zack = zackrank.ZackRank()
        self.fileName = ""
        self.rc = 3 # rank criteria <=3

    def checkCriteria(self, rankstr):
        try:
            rank = int(rankstr)
            if rank <= self.rc and rank > 0:
                return True
            else:
                return False                 
        except:
            return False
            
    def getOutputLine(self,symbol,rank,abr):
        idur = ""
        idutotal = ""
        etf = ""
        abrt = ""
        abr1w = ""
        abr1m = ""
        abr2m = ""
        abr3m = ""
        column=['indurank','indutotal','etf','abrt','abr1w','abr1m','abr2m','abr3m','numbr']
        colval=[]
        for colname in column:
            if colname in abr:
                colval.append(abr[colname])
            else:
                colval.append("")
                
        line = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % \
                (symbol,rank,colval[0],colval[1],colval[2],\
                colval[3],colval[4],colval[5],colval[6],colval[7],colval[8])
        return line
        
    def usage(self):
        print "program -f symbollist.txt [-c 3]"
        print "update symbol abr for rank <=3"

        
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:c:", ["filename", "ticklist"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.fileName = arg
            elif opt in ("-c", "--criteria"):
                self.rc = int(arg)
                
        if (self.fileName == ""):
            self.usage()
            sys.exit()
        print self.fileName,"rank criteria<=",self.rc
        return

    def process(self):
        self.parseOption()
        self.loadZackRankCsv()
        
    def loadZackRankCsv(self):
        # symbol,rank,sector,industry
        fp = open(self.fileName,'r',-1)
        outputfn = self.outputpath + self.abrname + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        outputfp = open(outputfn,'w',-1)
        header = 'symbol,rank,indurank,indutotal,etf,abrt,abr1w,abr1m,abr2m,abr3m,numbr\n'
        outputfp.write(header)
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            symbol = row[0]
            rankstr = row[1]
            retabr = {}
            if self.checkCriteria(rankstr):                
                retabr = self.zack.getBrokerRecom(symbol)
            
            line = self.getOutputLine(symbol,rankstr,retabr)
            print idx,line
            idx += 1
            outputfp.write(line)
            if idx%10 == 0:
                outputfp.flush()
        fp.close()      # closing
        outputfp.close()
        return
        
if __name__ == "__main__":
    obj = UpdateZackAbr()
    obj.process()
        