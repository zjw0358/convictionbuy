'''
5 minute:
http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=aapl&type=5&___qn=3

60 minute:
http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=aapl&type=60&___qn=3

last hour close price is slight different from yahoo EOD

[{"d":"2015-09-10 10:30:00","o":"110.0200","h":"111.5180","l":"109.9300","c":"111.4460","v":"9061662"},{"d":"2015-09-10 11:30:00","o":"111.4800","h":"112.5650","l":"111.4800","c":"112.1090","v":"5850770"},{"d":"2015-09-10 12:30:00","o":"112.1100","h":"112.7450","l":"112.0800","c":"112.3500","v":"3347158"},{"d":"2015-09-10 13:30:00","o":"112.2500","h":"112.9000","l":"112.2500","c":"112.9000","v":"2445339"},
'''

#import json
#from pprint import pprint
import pandas

class SinaMarketData:
    #only hour data until yesterday close
    def reqHisData(self,symbol,param=""):
        freq='60'
        if ("5m" in param):
            freq = "5"
        
        url = "http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=%s&type=%s&___qn=3" % (symbol,freq)
        #print param,url
        df = pandas.read_json(url)
        df.rename(columns={'d': 'Date','c': 'Close','h':'High','l':'Low','o':'Open','v':'Volume'}, inplace=True)
        df['Adj Close'] = df['Close']
        df.set_index('Date',inplace=True)
        return df
                   
    def reqLastDataRT(self,symbol):
        url = "http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=%s&type=5&___qn=3" % (symbol)
        df = pandas.read_json(url)
        df.rename(columns={'d': 'Date','c': 'Close','h':'High','l':'Low','o':'Open','v':'Volume'}, inplace=True)
        df['Adj Close'] = df['Close']
        df.set_index('Date',inplace=True)
        row = df.tail(1)
        #print row
        return row
        pass
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = SinaMarketData()
    #obj.reqHisData("aapl")
    obj.reqLastDataRT("aapl")