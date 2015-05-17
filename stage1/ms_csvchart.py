'''
chart tool
    draw chart according to input data(dataframe)
    
input data format
    csv
    symbol,col1,col2,col3
    
example:    
    run ms_chart.py -f data.csv    
'''
import getopt
import sys
import matplotlib.pyplot as plt
import pandas
import csv
import marketdata
from collections import OrderedDict

class ms_csvchart:
    def __init__(self):
        self.fileName=""
        self.mtd = marketdata.MarketData()
        return
        
    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:h",["filename","help"])
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
        for opt, arg in opts:
            if opt in ("-f", "--filename"):#symbol file
                self.fileName = arg
            elif opt in ("-h"):
                self.usage()
                sys.exit()
        if self.fileName=="":
            self.usage()            
            sys.exit()    
        print "input file=",self.fileName
        return 
            
    #usage
    def usage(self):
        print "run ms_csvchart -f data.csv"

    def loadCsvFile(self,fileName):
        print  "Loading data csv file..."
        allLst = OrderedDict()
        header=[]
        #table = pandas.DataFrame(allLst,columns=self.allcols)
        
        fp = open(fileName,'r',-1)
        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                #header
                idx += 1
                for rowid, item in enumerate(row):            
                    lst = []
                    allLst[item] = lst
                    header.append(item)
                print "number of columns =",len(allLst) 
                continue
            for rowid, item in enumerate(row):            
                lst = allLst[header[rowid]]
                #if rowid>1:
                item=item.replace(" ","")
                lst.append(self.mtd.tofloat(item))
                #else:
                #lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=header)
        return table
        
    def drawChart(self,df):
        '''
        for index, row in df.iterrows():
            symbol = df.loc[index,'px']
            symbol = row['symbol']
            print "processing ",index, symbol
        '''
        #print len(df.index)
        '''
        for idx in range(0,len(df.index)):            
            symbol = df.iloc[idx,0]
            ser = df.iloc[idx,1:]
            print ser
            ser.plot()
            print symbol
        ''' 
        #first column is legend
        #print dfb.isdeci
        #nsflag = False
        offset = 2
        xtickname = list(df.columns.values[offset:])
        
        for row in df.iterrows():
            index, data = row
            lst = data.tolist()
            #print lst
            '''
            if nsflag==False:
                for idx in range(0,len(lst)):
                    #print lst[idx],lst[idx].isdigit()
                    #if lst[idx].isdigit()==True:
                    if self.mtd.isNumber(lst[idx]):
                        nsflag=True                        
                        offset = idx
                        print "True offset=",offset
                        break
            print lst[offset:]
            '''
            plt.plot(lst[offset:],label=data[0])
        plt.xticks(range(len(xtickname)),xtickname);            
        plt.legend()
        plt.show()                                
    def cmdline(self):
        self.parseOption()
        df = self.loadCsvFile(self.fileName)
        self.drawChart(df)
        return
        
if __name__ == "__main__":
    obj = ms_csvchart()
    obj.cmdline()    
        