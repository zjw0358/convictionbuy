#http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=aapl&type=60&___qn=3
'''
[{"d":"2015-09-10 10:30:00","o":"110.0200","h":"111.5180","l":"109.9300","c":"111.4460","v":"9061662"},{"d":"2015-09-10 11:30:00","o":"111.4800","h":"112.5650","l":"111.4800","c":"112.1090","v":"5850770"},{"d":"2015-09-10 12:30:00","o":"112.1100","h":"112.7450","l":"112.0800","c":"112.3500","v":"3347158"},{"d":"2015-09-10 13:30:00","o":"112.2500","h":"112.9000","l":"112.2500","c":"112.9000","v":"2445339"},
'''

#import json
#from pprint import pprint
import pandas

class SinaMarketData:
    def reqHisData(self,symbol):
        url = "http://stock.finance.sina.com.cn/usstock/api/json.php/US_MinKService.getMinK?symbol=%s&type=60&___qn=3" % (symbol)
        df = pandas.read_json(url)
        df.rename(columns={'d': 'Date','c': 'Close','h':'High','l':'Low','o':'Open','v':'Volume'}, inplace=True)
        df['Adj CLose'] = df['Close']
        df.set_index('Date',inplace=True)
        return df        
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = SinaMarketData()
    obj.reqHisData("aapl")