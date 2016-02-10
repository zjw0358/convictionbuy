import urllib2
import json

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
'''
class GoogleMarketDataRT:
    # return dataframe
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
            '''
            print outer[0]['el']
            inner = json.dumps(outer[0])
            obj = json.loads(inner)
            return obj
            '''
        except:
            return ""
        

if __name__ == "__main__":
    c = GoogleMarketDataRT()    
    quote = c.reqHisData("AAPL","O")
    print quote['el']        
                