from feed_sina import SinaMarketData
from feed_yahoo import FeederYahoo
from feed_google import FeederGoogle
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
        self.sinaapi = SinaMarketData()
        self.yahoofeed = FeederYahoo()
        self.googfeed = FeederGoogle()
        self.datacfg = ms_config.MsDataCfg("")
        self.cachepath = self.datacfg.getDataConfig("cache", "../cache/")
        pass
     
    def initOption(self, params):                
        self.app_param = params
        self.ohlcid = 0

    def _downloadOhlc(self, symbol, sinasymbol, googsymbol, googexg):
        self.downloadid += 1        
        if self.app_param.verbose > 0:
            start = timer()
            s = 'downloading %d %s' % (self.downloadid, symbol)
            sys.stdout.write(s)      
            # print "downloading ",self.downloadid, symbol
        
        #try:
        if "sina" in self.app_param.feed:
            ohlc = self.sinaapi.reqHisData(sinasymbol, self.app_param.feed)
        elif "yahoo" in self.app_param.feed:
            ohlc = self.yahoofeed.reqHisData(symbol, self.app_param.feed, self.app_param.start_date, self.app_param.end_date)
        elif "goog" in self.app_param.feed:
            ohlc = self.googfeed.reqMarketData(googsymbol, googexg, self.app_param.feed)
        else:
            ohlc = web.get_data_yahoo(symbol, self.app_param.start_date, self.app_param.end_date)

        self.saveOhlc(symbol, ohlc, self.app_param.feed)
            
        #except:
        #    self.numError += 1
        #    print "System/Network Error when retrieving ",symbol," skip it"
        #    return None

        if (self.app_param.verbose > 0):
            end = timer()
            print "\ttime",round(end - start,3)
            
        return ohlc
        
    # download the whole table , for self run program           
    def _downloadAll(self, table):
        self.numError = 0
        self.downloadid = 0
        for index, row in table.iterrows():
            symbol = row['symbol']
            goog = row['goog']
            googexg = row['googexg']
            sina =  row['sina']            
            ohlc = self._downloadOhlc(symbol,sina,goog,googexg)  
            #if (ohlc is None):
        #if (self.app_params.verbose>1):
        #    print table
        return table
        pass        

    # argstr is a string
    # split it
    # TODO should be savemd by default
    def download(self, argstr=""):

        if (argstr==""):
            args = sys.argv[1:]
        else:
            args= argstr.split()
        param_parser = ms_paramparser.ms_paramparser()
        app_param = param_parser.parseOption(args)
        self.initOption(app_param)
        #df1 = app_params.getSymbolDf()
        df1 = self.mtd.get_symbol_df(app_param)
        
        print "ms_feed downloading..."
        start = timer()
        self._downloadAll(df1)
        end = timer()
        print "\tfinished with time",round(end - start,3)
 
    def getOhlc(self,symbol,sinasymbol,googsymbol,googexg):   
        self.ohlcid += 1
        if (self.app_param.verbose > 1):
            start = timer()
            s = "loading from cache %d %s." % (self.ohlcid, symbol)
            sys.stdout.write(s)      

        #print "loading from cache ",self.ohlcid, symbol  
        
        ohlc = self.loadOhlc(symbol)
        if ohlc.empty:
            print symbol," marketdata is not in cache, skip it"
            return None
        if (self.app_param.verbose > 1):
            end = timer()  
            print "\ttime",round(end - start,3)
            
        return ohlc

    
    # download the whole table , for self run program           
    def getOhlcAll(self, table):
         #TODO if no post-module, should return immediately
        self.numError = 0
        #id = 0
        for index, row in table.iterrows():
            symbol = row['symbol']
            goog = row['goog']
            googexg = row['googexg']
            sina = row['sina']
            
            ohlc = self.getOhlc(symbol,sina,goog,googexg)  
            if (ohlc is None):
                continue            
        return table
        pass
    
    # TODO, if time range is null then load all  
    def loadOhlc(self, symbol):
        filename = self.cachepath + symbol + "_ohlc_" + self.app_param.feed + ".csv"
        if self.app_param.verbose > 1:
            sys.stdout.write(filename) 
            # print "loading",filename

        try:
            ohlc = pandas.read_csv(filename,index_col=['Date'])
        except:
            ohlc = pandas.DataFrame()
            return ohlc
            
        # for sina 1H/5m data, load all
        if "sina" in self.app_param.feed or "goog" in self.app_param.feed:
            if self.app_param.tail_offset > 0:
                ohlc.drop(ohlc.tail(self.app_param.tail_offset).index, inplace=True)
            return ohlc
        
        ohlc.index = pandas.to_datetime(ohlc.index)  
        date1 = datetime.datetime.strptime(self.app_param.start_date, '%Y-%m-%d')
        date2 = datetime.datetime.strptime(self.app_param.end_date, '%Y-%m-%d')
        # print date1,date2
        # unable to get next business day
        start = -1
        end = -1
        for idx, item in enumerate(ohlc.index):
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
        ohlc = self.mtd.adjClosePrice(ohlc)
        filename = self.cachepath + symbol + "_ohlc_" + feedname + ".csv"
        try:
            os.remove(filename)
        except:
            #print "unable to delete file",filename
            pass
        ohlc.to_csv(filename,sep=',')
        pass
        
if __name__ == "__main__":
    obj = ms_feed()
    obj.download()
