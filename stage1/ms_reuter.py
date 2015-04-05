'''
marketscan module
- filter by reuter fundamental data

use case:    
run marketscan -g "ms_reuter" -t "LLY,NVS,JNJ,BMY,GILD,MRK,PFE,IBB,ABBV,ANT,BIIB,AMGN,AZN"

'''
import reuterfunda
import pandas
import datetime
import re
from collections import OrderedDict

class ms_reuter:
    def __init__(self):
        self.reuter = reuterfunda.ReuterFunda()
        self.reuterFile = "./msdata_reuter_2015-01-27.csv"
        return        

    def loadData(self,fileName):
        df = self.reuter.loadReuterCsvFile(self.reuterFile)
        return df
        
    def parseParam(self,param):
        return
    
    def saveTableFile(self,table,addstr=""):
        saveFileName = "scan_"
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

    def process(self,tablein,param):
        ticklist = tablein['symbol']
        print tablein
        #criteria
        
        criteria = []
        outputcol = []
        coldict = OrderedDict()
        for op in param:
            criteria.append(op)
        # filter by dynamic criteria string
        crstr = ""
        pattern1 = "([\w]+)([><])([\d]+)"  #cppettm < 20
        pattern2 = "([\d\D]+)([><])([\d\D]+)"  #saleqtr0 > saleqtr1
        for cr in criteria:
            an = re.match(pattern1,cr)            
            if an!=None:
                cr0 = "(df['%s']%s%s) & " % (an.group(1),an.group(2),an.group(3))
                crstr += cr0
            else:
                an = re.match(pattern2,cr)
                if an!=None:
                    cr0 = "(df['%s']%sdf['%s']) & " % (an.group(1),an.group(2),an.group(3))
                    crstr += cr0
                    coldict[an.group(1)] = 0
                    coldict[an.group(3)] = 0
                                                        
        crstr += "(1)"
        print "reuter criteria = ", crstr
        
                
        # test code        
        df = self.loadData(self.reuterFile)
        #df = df[(df['symbol'].isin(ticklist)) & (df['saleqtr0']>df['saleqtr-1'])]
        
        
        outputcol = coldict.keys() + self.reuter.colbase
        
        df1 = df[df['symbol'].isin(ticklist) & eval(crstr) ][outputcol]
        
        #print df1
        
        tableout = pandas.merge(tablein,df1,how="inner")
        return tableout
      
        
    def test(self):
        ticklist = ['LLY','BMY','ABBV','GILD','PFE','MRK','JNJ','GSK']
        self.process(ticklist,"")
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_reuter()
    obj.test()