import urllib2
import json
import time

class GoogleFinanceAPI:
    def __init__(self):
        self.prefix = "http://finance.google.com/finance/info?client=ig&q="

    
    def as_complex(self,dct):
        print "===complex==="
        print dct
        return dct
    
    def get(self,symbol,exchange):
        url = self.prefix+"%s:%s"%(exchange,symbol)
        u = urllib2.urlopen(url)
        content = u.read()
        print content[3:]
        
        outer = json.loads(content[3:])
        inner = json.dumps(outer[0])
        print inner
        print "===="
        obj = json.loads(inner)
        print type(obj),obj
        print "==="
        print obj['el']
        #print "==="
        #obj2 = json.loads(obj[0])
        #print obj2
        #dct = json.dumps(content[3:])
        #json.loads('{"__complex__": true, "real": 1, "imag": 2}',object_hook=as_complex)
        #print type(dct),dct
        #print type(obj),obj
        #for i in xrange(0,len(obj),2):
        #    print i,obj[i]

        #print "==="
        #print type(obj),obj,obj['el']
        #print "==="
        return obj[u'el']
        
    def test(self):
       #data = "{u'el': u'66.87', u'eccol': u'chr', u'ec': u'-2.07', u'l_fix': u'68.94', u'cp': u'0.54', u'id': u'656142', u'yld': u'2.79', u'el_fix': u'66.87', u'lt': u'Apr 22, 4:00PM EDT', u'ecp_fix': u'-3.00', u'elt': u'Apr 22, 7:59PM EDT', u'cp_fix': u'0.54', u'c_fix': u'0.37', u'pcls_fix': u'68.57', u'ecp': u'-3.00', u'div': u'0.48', u'l_cur': u'68.94', u'c': u'+0.37', u'e': u'NASDAQ', u'ltt': u'4:00PM EDT', u'l': u'68.94', u's': u'2', u't': u'QCOM', u'el_cur': u'66.87', u'lt_dts': u'2015-04-22T16:00:01Z', u'ec_fix': u'-2.07', u'ccol': u'chg'}"
       data = '{"el":"66.87"}'
       obj = json.loads(data,object_hook=self.as_complex)
       print type(obj),obj
       return
 
        
if __name__ == "__main__":
    c = GoogleFinanceAPI()    
    quote = c.get("QCOM","NASDAQ")
    #c.test()
    #print quote
