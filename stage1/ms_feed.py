from feed_sina import SinaMarketData
from feed_yahoo import FeederYahoo
import pandas.io.data as web
import pandas
from timeit import default_timer as timer
import datetime
import marketdata
import ms_paramparser
import ms_config
import sys
import os

class ms_feed:
    def __init__(self):
        self.mtd = marketdata.MarketData()
        self.datacfg = ms_config.MsDataCfg("")
        self.cachepath = self.datacfg.getDataConfig("folder","../cache/") 
        pass
     
    def initOption(self, params):
        self.params = params
        self.ohlcid = 0;   
        if ("sina" in params.feed):
            self.sinaapi = SinaMarketData()
        if ("yahoo" in params.feed):
            self.yahoofeed = FeederYahoo()

    # for self run 
    def process(self, args=""):
        #print "I am in!"
        #sys.exit()
        #args = sys.argv[1:]
        if (args==""):
            args = sys.argv[1:]        
        params = ms_paramparser.ms_paramparser()
        params.parseOption(args)
        self.initOption(params)
        if params.tickdf.empty:
            print "loading from symbolfile..."
            df = self.mtd.loadSymbolLstFile(params.symbolLstFile)
            df1 = self.mtd.getSymbolByPid(df,params.pid)[['symbol']]
            #ticklist = df1['symbol']
        else:
            print "using ticklist from command line..."            
            df1 = params.tickdf  
        #if (params.savemd):
        self.getOhlcAll(df1, params)
 
    # API for marketscan
    def getOhlc(self, symbol):
        start = timer()
        
        self.ohlcid += 1
        if (self.params.loadmd):
            print "loading from cache ",self.ohlcid, symbol  
            ohlc = self.loadOhlc(symbol)
            if ohlc.empty:
                print symbol," marketdata is not in cache, skip it"
                return None    
        else:
            print "downloading ",self.ohlcid, symbol       
            try:
                if ("sina" in self.params.feed):
                    ohlc = self.sinaapi.reqHisData(symbol)
                elif ("yahoo" in self.params.feed):
                    ohlc = self.yahoofeed.reqHisData(symbol,self.params.feed,self.params.startdate, self.params.enddate)
                else:
                    ohlc = web.get_data_yahoo(symbol, self.params.startdate, self.params.enddate)
            
                if (self.params.savemd): 
                    self.saveOhlc(symbol,ohlc,self.params.feed)
                
            except:
                self.numError += 1
                print "System/Network Error when retrieving ",symbol," skip it"
                return None
                '''
                if numError>3:
                    print "too many errors when downloading symbol data, exit now"
                    sys.exit()
                '''
        # adjust adj close price.
        ohlc = self.mtd.adjClosePrice(ohlc)       
        end = timer()  
        print "\ttime",round(end - start,3)
        return ohlc
        
    # download the whole table , for self run program           
    def getOhlcAll(self, table, params):
         #TODO if no post-module, should return immediately
        self.numError = 0
        #id = 0
        for index, row in table.iterrows():
            symbol = row['symbol']
            #print "downloading ",id, symbol
            #id+=1
            #start = timer()
            
            ohlc = self.getOhlc(symbol)  
            if (ohlc is None):
                continue
            # adjust adj close price.
            #ohlc = self.mtd.adjClosePrice(ohlc)       
            #end = timer()  
            #print "\ttime",round(end - start,3)
            #add 'px' column
            #print "intc",ohlc['Adj Close']
            #table.loc[index,'px'] = round(ohlc['Adj Close'][-1],2)
            #start = timer()
            #print "processing",symbol            
            #end = timer()  
            #print "\ttime",round(end - start,3)
        return table
        pass
        
    def loadOhlc(self,symbol):
        filename = self.cachepath + symbol + "_ohlc_" + self.params.feed + ".csv"
        print "loading",filename
        try:
            ohlc = pandas.read_csv(filename,index_col=['Date'])
        except:
            ohlc = pandas.DataFrame()
            return ohlc
            
        #for sina 1H data, load all
        if ("sina" in self.params.feed):
            return ohlc
        ohlc.index = pandas.to_datetime(ohlc.index)  
        date1 = datetime.datetime.strptime(self.params.startdate,'%Y-%m-%d')
        date2 = datetime.datetime.strptime(self.params.enddate,'%Y-%m-%d')
        #print date1,date2
        #unable to get next business day
        start = -1
        end = -1
        for idx,item in enumerate(ohlc.index):
            #print item,type(item)
            #print idx,item
            if (start==-1 and item >= date1):
                start = idx
                #print "start",item                
            if item >= date2:
                end = idx
                print "end",item
                break

        if (end==-1):
            end=len(ohlc.index)
        #print start,end
        ohlc = ohlc.iloc[start:end]
        return ohlc
          
    #save ohlc to csv file
    def saveOhlc(self, symbol, ohlc, feedname):
        #delete file firstly
        filename = self.cachepath + symbol + "_ohlc_" + feedname + ".csv"
        try:
            os.remove(filename)
        except:
            print "unable to delete file",filename
            pass
        ohlc.to_csv(filename,sep=',')
        pass
        
if __name__ == "__main__":
    obj = ms_feed()
    obj.process()
         