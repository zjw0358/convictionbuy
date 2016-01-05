'''
5 minute:
http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=aapl&type=5&___qn=3

60 minute:
http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=aapl&type=60&___qn=3

[{"d":"2015-09-10 10:30:00","o":"110.0200","h":"111.5180","l":"109.9300","c":"111.4460","v":"9061662"},{"d":"2015-09-10 11:30:00","o":"111.4800","h":"112.5650","l":"111.4800","c":"112.1090","v":"5850770"},{"d":"2015-09-10 12:30:00","o":"112.1100","h":"112.7450","l":"112.0800","c":"112.3500","v":"3347158"},{"d":"2015-09-10 13:30:00","o":"112.2500","h":"112.9000","l":"112.2500","c":"112.9000","v":"2445339"},
'''


import pandas
import pandas.io.data as web
import datetime
import urllib2
import csv
import sys
import feed_sina

class FeederYahoo:
    def __init__(self):
        self.numError = 0
        self.sina = feed_sina.SinaMarketData()
    '''   
    def reqHisData0(self,symbol,startdate="",enddate=""):
        ohlc = web.get_data_yahoo(symbol, startdate, enddate)
        print ohlc
        ohlc = ohlc.asfreq('W-FRI',method='pad')
        print ohlc
        return
        ohlc
    '''    
    def reqHisData(self,symbol,param="",startdate="",enddate=""):
        #http://ichart.finance.yahoo.com/table.csv?s=xle&a=01&b=19&c=2014&d=01&e=19&f=2015&g=d&ignore=.csv
        if (enddate == ""):
            enddate = datetime.datetime.now().strftime("%Y-%m-%d")

        if (startdate == ""):
            startdate = (datetime.datetime.now() - datetime.timedelta(days=730)).strftime("%Y-%m-%d")
            
            
        endt = datetime.datetime.strptime(enddate,'%Y-%m-%d')
        startt = datetime.datetime.strptime(startdate,'%Y-%m-%d')
        freq = "d"
        
        if ("week" in param):
            freq = "w"
        elif ("month" in param):
            freq = "m"
        elif ("drt" in param): # daily realtime
            return self.reqDailydataRT(symbol,startdate,enddate)            
        else:
            return self.reqDailydata(symbol,startdate,enddate)
            
        #abc -> start date
        #def -> end date
        url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%02d&b=%02d&c=%04d&d=%02d&e=%02d&f=%04d&g=%s&ignore=.csv" \
            % (symbol,startt.month-1,startt.day,startt.year,endt.month-1,endt.day,endt.year,freq)

        try:            
            #page = urllib2.urlopen(url).read()
            response = urllib2.urlopen(url)

        except:
            print "unable to open url",url
            return 
        
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
                if idx==0:
                    idx += 1
                    continue
                #print row
                dateLst.append(row[0])
                openLst.append(float(row[1]))
                highLst.append(float(row[2]))
                lowLst.append(float(row[3]))
                closeLst.append(float(row[4]))
                volumeLst.append(int(row[5]))
                adjCloseLst.append(float(row[6]))
                idx += 1
        except:
            print "error when reading csv data, exit..."
            return 
        dateLst.reverse()
        openLst.reverse()
        highLst.reverse()
        lowLst.reverse()
        closeLst.reverse()
        volumeLst.reverse()
        adjCloseLst.reverse()
        ohlc = pandas.DataFrame({'Open':openLst,'High':highLst,'Low':lowLst,\
            'Close':closeLst,'Volume':volumeLst,'Adj Close':adjCloseLst},\
            columns=['Open','High','Low','Close','Volume','Adj Close'],index = dateLst)        
        ohlc.index.name = 'Date'
        return ohlc
        
    def reqDailydata(self,symbol,startdate,enddate):
        try:
            ohlc = web.get_data_yahoo(symbol, startdate, enddate)
        except:
            self.numError += 1
            print "System/Network Error when retrieving ",symbol," skip it"
            if self.numError>3:
                print "too many errors when downloading symbol data, exit now"
                sys.exit()
        return ohlc
        
    # history data + latest RT data    
    def reqDailydataRT(self,symbol,startdate,enddate):
        df1 = self.sina.reqLastDataRT(symbol)
        try:
            ohlc = web.get_data_yahoo(symbol, startdate, enddate)
        except:
            self.numError += 1
            print "System/Network Error when retrieving ",symbol," skip it"
            if self.numError>3:
                print "too many errors when downloading symbol data, exit now"
                sys.exit()
        
        # real time data from sina
        #print df1
        ohlc = ohlc.append(df1)
        return ohlc
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = FeederYahoo()
    #print obj.reqHisData("abt","week","2015-10-01","2015-11-11")
    print obj.reqDailydataRT("abt","2015-10-01","2016-01-03")