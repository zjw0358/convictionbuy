import csv
import datetime
import fundata
import sys
import getopt
import pandas

'''
used to update fundamental data periodly
updatefunda.py -f ../data/allsymbolhaverank.csv 
output - ../data/fundaupdate_[time].csv
'''
#TODO check ETF
class UpdateFunda:
    def __init__(self):
        self.outputpath = "../data/"
        self.sufname = "fundaupdate_"
        self.fileName = ""
        self.rc = [1,2,3] # rank criteria <=3
        self.funda = fundata.FundaData()
        
    def checkCriteria(self, rankstr):
        try:
            rank = int(rankstr)
            if rank in self.rc:
                return True
            else:
                return False                 
        except:
            return False
            
        
    def usage(self):
        print "program -f symbollist.txt [-c 3]"
        print "update symbol fundamental data for rank <=3"

        
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
        # symbol,rank
        fp = open(self.fileName,'r',-1)
        ticklist=[]
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            ticklist.append(row[0]) #symbol
            idx += 1
        fp.close()      # closing
        psLst = self.funda.getPriceSale(ticklist)
        print ticklist
        print "======"
        print psLst
        #output
        self.fundatable=pandas.DataFrame({'symbol':ticklist,'pricesale':psLst},\
            columns=['symbol','pricesale'])
        outputfn = self.outputpath + self.sufname + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'       
        self.fundatable.to_csv(outputfn,sep=',',index=False)
        
        
    
if __name__ == "__main__":
    obj = UpdateFunda()
    obj.process()
        