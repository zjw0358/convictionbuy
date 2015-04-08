import getopt
import datetime
import sys
import csv
import pandas

# evaluation criteria on the fly
from collections import OrderedDict
import re
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

    def tofloat(self,item):
        #print item
        if item=="N/A" or item=="" or item=="NA":
            return 0
        elif item[-1]=="K":
            return float(item.replace("K",""))*1000
        elif item[-1]=="M":
            return float(item.replace("M",""))*1000000
        elif item[-1]=="B":
            return float(item.replace("B",""))*1000000000
        elif item[-1]=="T":
            return float(item.replace("T",""))*1000000000000
        else:
            return float(item)
    #version1       
    def evalCriteria1(self, df, param, colsin):
        criteria = []
        outputcol = []
        coldict = OrderedDict()
            
        for op in param:
            criteria.append(op)
            
        if not criteria:
            print "criteria is empty,...return original table"
            return df
        # construct unique column name    
        for colnm in colsin:
            coldict[colnm] = 0
            
        # filter by dynamic criteria string
        crstr = ""
        pattern1 = "([\w]+)([><])([-+]?[0-9]*\.?[0-9]+)"  #cppettm < 20.00 (float)
        pattern2 = "([\d\D]+)([><])([^[A-Za-z0-9_]+$])"  #saleqtr0 > saleqtr1
        #pattern3 = "([a-z][a-z0-9-]*)" # select column only

        for cr in criteria:            
            an = re.match(pattern1,cr)            
            if an!=None:
                print "criteria matched lvalue <> float"
                cr0 = "(df['%s']%s%s) & " % (an.group(1),an.group(2),an.group(3))
                crstr += cr0
                coldict[an.group(1)] = 0
            else:
                an = re.match(pattern2,cr)
                if an!=None:
                    print "criteria matched lvalue <> string"
                    rstr = an.group(3)
                    print float(rstr)
                    cr0 = "(df['%s']%sdf['%s']) & " % (an.group(1),an.group(2),an.group(3))
                    crstr += cr0
                    coldict[an.group(1)] = 0
                    coldict[an.group(3)] = 0
                else: #select column
                    coldict[cr] = 0
                                                        
        crstr += "(1)"
        print "to evaluate criteria = ", crstr
        outputcol = coldict.keys()
        if crstr == "(1)":
            df = df[outputcol]
        else:
            df = df[eval(crstr)][outputcol]
        return df
        
    #version2
    def evalCriteria(self, df, param, colsin):
        criteria = []
        outputcol = []
        coldict = OrderedDict()
            
        for op in param:
            criteria.append(op)
            
        if not criteria:
            print "criteria is empty,...return original table"
            return df
        # construct unique column name    
        for colnm in colsin:
            coldict[colnm] = 0
            
        # filter by dynamic criteria string
        crstr = ""
        pattern1 = "([a-z][a-z0-9-]*)"
        pattern2 = "[></]"
        #pattern1 = "([\w]+)([><])([-+]?[0-9]*\.?[0-9]+)"  #cppettm < 20.00 (float)
        #pattern2 = "([\d\D]+)([><])([^[A-Za-z0-9_]+$])"  #saleqtr0 > saleqtr1
        #pattern3 = "([a-z][a-z0-9-]*)" # select column only

        for cr in criteria:
            collst = re.findall(pattern1,cr)
            ration = re.findall(pattern2,cr)
            if len(ration)!=0:
                cr0 = re.sub(pattern1,r"df['\1']",cr)
                if crstr=="":
                    crstr = crstr + "(" + cr0 + ") "
                else:
                    crstr = crstr + "& (" + cr0 + ") "
            # add column to display
            for col in collst:
                coldict[col] = 0
                
                                                        
        #crstr += "(1)"
        print "to evaluate criteria = ", crstr
        outputcol = coldict.keys()
        if crstr == "":
            df = df[outputcol]
        else:
            df = df[eval(crstr)][outputcol]
        return df
        
    #save table
    def saveTableFile(self,table,addstr=""):
        saveFileName = "mdscan_"
        for sgyname in self.sgyInx:
            saveFileName += sgyname
            saveFileName +="_"
            
        if addstr != "":
            saveFileName = saveFileName + addstr + "_"
            
    
        outputFn = self.outputpath + saveFileName + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        try:
            table.to_csv(outputFn,sep=',',index=False)
            print "Finish wrote to ",outputFn
        except:
            print "exception when write to csv ",outputFn
