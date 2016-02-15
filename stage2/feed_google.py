import urllib2
#import json
import pandas
import csv
import marketdata
import ms_config

class FeederGoogle:
    def __init__(self):
        self.mtd = marketdata.MarketData()
        cfg = ms_config.MsDataCfg("") 
        symbolLstFile = cfg.getDataConfig("marketdata")
        df = self.mtd.loadSymbolLstFile(symbolLstFile)
        self.googdict = df.set_index('goog')['googexg'].to_dict()
        '''
        for key in self.googdict:
            if (self.googdict[key]!=""):
                print key,self.googdict[key]
        '''
        pass
    '''
    # for 15m data
    http://www.networkerror.org/component/content/article/1-technical-wootness/44-googles-undocumented-finance-api.html
    EXCHANGE%3DSGX
    MARKET_OPEN_MINUTE=540
    MARKET_CLOSE_MINUTE=1020
    INTERVAL=300
    COLUMNS=CLOSE,HIGH,LOW,OPEN,VOLUME
    DATA_SESSIONS=[MORNING,540,750],[AFTERNOON,840,1020]
    DATA=
    TIMEZONE_OFFSET=480
    2.6,2.6,2.6,2.6,100
    http://www.google.com/finance/getprices?i=3600&p=30d&f=d,o,h,l,c,v&df=cpct&q=AAPL
    '''
    def reqMarketData(self,symbol,exg,param=""):
        freq = '300'
        duration='10d'
        if ('1h' in param):
            freq='3600'
            duration='30d'
        elif ('15m' in param):
            freq='900'
            duration='20d'
        
        url = "http://www.google.com/finance/getprices?i=%s&p=%s&f=o,h,l,c,v&df=cpct&q=%s" % (freq,duration,symbol)
        #exg = self.googdict[symbol]
        if (exg!=""):
            url=url+"&x="+exg
     
        #print url   
        try:
            response = urllib2.urlopen(url)
        except:
            print "unable to open url",url
            return 
        
        flag = False
        
        dateLst = []
        openLst = []
        highLst = []
        lowLst = []
        closeLst = []
        volumeLst = []
        adjCloseLst = []
        
        reader = csv.reader(response)
        idx = 0
        try:
            for row in reader:
                if (not flag):
                    if ("TIMEZONE_OFFSET" in row[0]):
                        flag = True
                        idx = 0
                        continue
                    else:
                        idx += 1                    
                        continue

                dateLst.append(idx)
                closeLst.append(float(row[3]))
                highLst.append(float(row[1]))
                lowLst.append(float(row[2]))
                openLst.append(float(row[0]))
                volumeLst.append(int(row[4]))
                adjCloseLst.append(float(row[3]))
                idx += 1
        except:
            print "error when reading google data, exit..."
            return
            
        #dateLst.reverse()
        #openLst.reverse()
        #highLst.reverse()
        #lowLst.reverse()
        #closeLst.reverse()
        #volumeLst.reverse()
        #adjCloseLst.reverse()
        
        ohlc = pandas.DataFrame({'Open':openLst,'High':highLst,'Low':lowLst,\
            'Close':closeLst,'Volume':volumeLst,'Adj Close':adjCloseLst},\
            columns=['Open','High','Low','Close','Volume','Adj Close'],index = dateLst)        
        ohlc.index.name = 'Date'
        #print ohlc
        return ohlc
        pass
    '''
    d : Internal Google Security ID
    t : Ticker
    e : Exchange Name
    l : Last Price
    l_cur : ???
    ltt : Last Trade Time
    ltt : Last Trade Date/Time
    c : Change (in ccy) - formatted with +/- cp : Change (%)
    ccol :
    el : Last Price in Extended Hours Trading
    el_cur :
    elt: Last Trade Date/Time in Extended Hours Trading
    ec : Extended Hours Change (in ccy) - formatted with +/-
    ec : Extended Hours Change (%)
    eccol :    
    def reqHisData(self,symbol,exg):        
        exchange=""
        if exg == "N":
            exchange = "NYSE"
        elif exg == "O":
            exchange = "NASDAQ"
        elif exg == "A":
            exchange = "NYSEMKT"
            

        url = "http://finance.google.com/finance/info?client=ig&q=%s:%s" % (exchange,symbol)
        try:
            u = urllib2.urlopen(url)
            content = u.read()
            #print content
            outer = json.loads(content[3:])
            return outer[0]['el']
            
            #print outer[0]['el']
            #inner = json.dumps(outer[0])
            #obj = json.loads(inner)
            #return obj
            
        except:
            return ""
    '''
    

if __name__ == "__main__":
    c = FeederGoogle()  
    c.reqMarketData("AAPL")  
    #quote = c.reqHisData("AAPL","O")
    #print quote['el']        
                