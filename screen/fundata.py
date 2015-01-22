import pandas.io.data as web
import pandas
import datetime
import urllib2
import csv

'''
http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv

'''

class FundaData:
    def __init__(self):       
        '''
        self.startdate = ""
        self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
        startday = datetime.date.today() - datetime.timedelta(days=365)
        self.startdate = startday.strftime("%Y-%m-%d")
        '''
    def setDateRange(self,enddatestr):
        if enddatestr=="":
            enddate = datetime.datetime.now()
        else:
            enddate = datetime.datetime.strptime(enddatestr,'%Y-%m-%d')
            
        startday = enddate - datetime.timedelta(days=365)
        self.enddate = enddatestr
        self.startdate = startday.strftime("%Y-%m-%d")
            
    def getPerf(self,symbol, param, enddatestr=""):
        ret = {}
        self.setDateRange(enddatestr)
        try:
            ohlc = web.get_data_yahoo(symbol, self.startdate, self.enddate)
        except:
            # IO error
            print "System/Network Error when retrieving ",symbol," skip it"
            return ret
        # calculate perf
        # print symbol
        px = ohlc['Adj Close']
        p1d = 0
        p4w = 0
        p12w = 0
        p24w = 0
        pmax = 0
        plen = len(px)
        if plen >= 2:
            p1d = round((px[-1]/px[-2] - 1)*100,2)    
        if plen >= 4*7:
            p4w = round((px[-1]/px[-4*7] - 1)*100,2)
        if plen >= 12*7:
            p12w = round((px[-1]/px[-12*7] - 1)*100,2)
        if plen >= 24*7:
            p24w = round((px[-1]/px[-24*7] - 1)*100,2)
        if len(px) >= 1*7:
            p1w = round((px[-1]/px[-1*7] - 1)*100,2)

        pmax = round((px[-1]/px[0] - 1) * 100,2)

        if 'vol20' in param:
            sma20vol = pandas.stats.moments.rolling_mean(ohlc['Volume'],20)
            ret['vol20'] = sma20vol[-1]
            
        if 'vol' in param:            
            ret['vol'] = ohlc['Volume'][-1]
            
        if 'px' in param:            
            ret['px'] = ohlc['Adj Close'][-1]
                      
        if 'ma10' in param:
            sma10s = pandas.stats.moments.rolling_mean(px,10)
            ret['ma10'] = round(sma10s[-1],2)
        
        if 'ma50' in param:            
            sma50s = pandas.stats.moments.rolling_mean(px,50)            
            ret['ma50'] = round(sma50s[-1],2)
            
        if 'ma200' in param:                        
            sma200s = pandas.stats.moments.rolling_mean(px,200)
            ret['ma200'] = round(sma200s[-1],2) 

        ret['p1d'] = p1d
        ret['p1w'] = p1w  
        ret['p4w'] = p4w
        ret['p12w'] = p12w
        ret['p24w'] = p24w
        


        return ret
        
    #limit=200               
    def getPriceSale(self, ticklist):
        symstr = ""
        limit = 199 #yahoo limit is 200
        lenlist = len(ticklist)
        stockps = []
        retidx= 0 
        for idx, symbol in enumerate(ticklist):
            symstr += symbol
            if idx<(lenlist-1) and (idx%limit!=0):
                symstr +="+"
                
            if idx%limit==0:
                print idx,symstr
                url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + "&f=p5"
                response = urllib2.urlopen(url)
                cr = csv.reader(response)
                for row in cr:
                    stockps.append(row[0]) 
                    retidx +=1
                symstr=""
                
        if symstr!="":
            print "last get",symstr
            url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + "&f=p5"
            response = urllib2.urlopen(url)
            cr = csv.reader(response)
            for row in cr:
                stockps.append(row[0])
                retidx +=1
                
        return stockps
        '''url = "http://finance.yahoo.com/d/quotes.csv?s=" + symbol + "&f=p5"
        page = urllib2.urlopen(url).read()
        #ps = float(page)
        #print symbol,"ps=",ps
        #return ps
        print page
        '''
    
          
    def process(self):
        return
        
if __name__ == "__main__":
    obj = FundaData()
    obj.process()