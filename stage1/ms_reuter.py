'''
marketscan module
- filter by reuter fundamental data

use case:    
run marketscan -g "ms_reuter"

'''
import reuterfunda
import pandas

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

    def process(self,ticklist,param):
        # test code        
        df = self.loadData(self.reuterFile)
        #print df
        df1 = df[df['symbol'].isin(ticklist)][self.reuter.colbase]
        print df1
        #return ticklist
        return df1['symbol']
        
    def test(self):
        ticklist = ['LLY','BMY','ABBV','GILD','PFE','MRK','JNJ','GSK']
        self.process(ticklist,"")
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ms_reuter()
    obj.test()