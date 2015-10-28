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
import numpy as np
import math
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
        
    def drawLineChart(self,df):
        #first column is legend
        # 0 -> nan
        df = df.replace(0, np.inf)
        offset = 1
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
        #plt.yticks(range(ymin,ymax))
        #plt.yticks(np.arange(ymin, ymax, 0.2), fontsize=10)
        legend = plt.legend(loc='upper left', shadow=True)        
        frame = legend.get_frame()
        frame.set_facecolor('0.90')       
        #plt.legend()
        plt.show()   

    def heatmap(self, df, cmap=plt.cm.gray_r):
        #fig = plt.figure()
        #ax = fig.add_subplot(111)
        #axim = ax.imshow(df.values, cmap=cmap, interpolation='nearest')
        fig, ax = plt.subplots()
        heatmap = ax.pcolor(df.as_matrix(), cmap=plt.cm.Blues)

        ax.set_xlabel(df.columns.name)
        ax.set_xticks(np.arange(len(df.columns)))
        ax.set_xticklabels(list(df.columns))
        ax.set_ylabel(df.index.name)
        ax.set_yticks(np.arange(len(df.index)))
        ax.set_yticklabels(list(df.index))
        #plt.colorbar(axim)                           
        plt.show()
        
    def setupParam(self,param):
        # scatter draw range
        self.xmin = 5
        self.xmax = 99
        self.ymin = 5
        self.ymax = 99
        self.zmin = 15
        self.zmax = 85
        
        if 'xmin' in param:
            self.xmin = param['xmin']
        if 'xmax' in param:
            self.xmax = param['xmax']
        if 'ymin' in param:
            self.ymin = param['ymin']
        if 'ymax' in param:
            self.ymax = param['ymax']
        if 'zmax' in param:
            self.zmax = param['zmax']
        if 'zmin' in param:
            self.zmin = param['zmin']
            
        print "draw range", self.xmin,self.xmax,self.ymin,self.ymax,self.zmin,self.zmax

    def drawChart(self,df,arg=""):
        #parse parameter
        param={}
        if arg!="":
            for item in arg.split(","):
                tokens=item.split("=")
                if len(tokens)>1:
                    param[tokens[0]] = int(tokens[1])        
                else:
                    param[tokens[0]] = ""
        self.setupParam(param)            
        
        if 'scatter' in param:
            self.drawScatter(df)
        else:
            pass
            #self.drawLineChart(df)        
            #self.heatmap(df)
            #print df.values
            #print df.as_matrix()
        return

    def drawScatter(self,df):
        #self.setupParam(arg)
        offset=1
        cols = list(df.columns.values) #[offset:]
        mklst = ['s','o','^','x','v','h','D','d','4','p']                
        #marker
        # s = square, o=circle

        lenmk = len(mklst)
        lencol = len(cols)
        
        
        #print "max=",df[cols[3]].max()
        #print "min=",df[cols[3]].min()
        #col3upper = max(abs(df[cols[3]].min()),abs(df[cols[3]].max()))
        #col3ratio = 77
        #col12ratio = 80
        col3list = df[cols[3]].tolist()
        col3arr = np.array(col3list)
        col3upper0 = np.percentile(col3arr, self.zmin) 
        col3upper1 = np.percentile(col3arr, self.zmax) 
        col3upper = max(abs(col3upper0),abs(col3upper1))
        
        col2list = df[cols[2]].tolist()
        col2arr = np.array(col2list)
        col2upper0 = np.percentile(col2arr, self.ymin) 
        col2upper1 = np.percentile(col2arr, self.ymax) 

        col1list = df[cols[1]].tolist()
        col1arr = (np.array(col1list))
        col1upper0 = np.percentile(col1arr, self.xmin) 
        col1upper1 = np.percentile(col1arr, self.xmax)
        
        dprOn = True #display ratio on
        
        print "upper",col1upper0,col1upper1,col2upper0,col2upper1,col3upper
        sizebase = 650
        

        #col 0 symbol, 1-x,2-y,3-size
        #idx = 0
        for index,row in df.iterrows():
            label = row['symbol']
            col3val = row[cols[3]]
            #size = math.log(abs(ret*20))*40
            #idx += 1
            
            x = row[cols[1]]
            y = row[cols[2]]
            
            #if check and (x>maxx or y>maxy or x<minx or y<miny or ret<minr or ret>maxr):
            #    continue
            if dprOn and (x>col1upper1 or x<col1upper0 or y>col2upper1 or y<col2upper0):
                # or abs(ret)>col3upper)
                print "skip",label,x,y,col3val
                continue
            else:   
                if col3val>0:
                    color = 'green'                    
                else:
                    color='red'

                col3val1 = min(abs(col3val)/col3upper,1)
                size = col3val1*sizebase
                if lencol>4:
                    mker = mklst[int(row[cols[4]])%lenmk]
                    print label,size,mker
                else:
                    mker = mklst[0]
                
                plt.scatter(x,y,c=color,s=size,marker=mker)#s,o,^
                plt.annotate(label, xy = (x, y), xytext = (-20, 20),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        
        plt.ylabel(cols[2])
        plt.xlabel(cols[1])
        tl = "scatter chart - z=%s" % (cols[3])
        plt.title(tl)
        #plt.xticks(range(len(xtickname)),xtickname);
        #plt.yticks(range(ymin,ymax))
        #plt.yticks(np.arange(ymin, ymax, 0.2), fontsize=10)
        #legend = plt.legend(loc='upper left', shadow=True)        
        #frame = legend.get_frame()
        #frame.set_facecolor('0.90')       
        #plt.legend()
        plt.show()   
        return
          
    def cmdline(self):
        self.parseOption()
        df = self.loadCsvFile(self.fileName)
        self.drawChart(df)
        #self.drawScatter(df)
        return
        
if __name__ == "__main__":
    obj = ms_csvchart()
    obj.cmdline()    
        