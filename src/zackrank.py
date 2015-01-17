#from bs4 import BeautifulSoup
import urllib2
import re



from bs4 import BeautifulSoup



class ZackRank:
    def __init__(self):
        #self.earning_exp = '^window.app_data_earnings[\d\D]*\\"data\\"[ :\\[]*(.*)]'
        self.rankPattern = '[\d\D]*Zacks Rank : (.*) <sup class=[\d\D]*'
        
        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' "
        print "example:run zackrank.py -t aapl"
        print "example:run zackrank.py -p portfolio.txt"

        
    def getRank(self,ticklist):
        zackranks = {}
        for symbol in ticklist:
            url = "http://www.zacks.com/stock/quote/"+symbol
            htmltxt =urllib2.urlopen(url).read()
            an = re.match(self.rankPattern, htmltxt)
            if an!=None:
                str1=an.group(1)
                if str1=='NA':
                    zrank = 0
                else:
                    zrank = int(str1[0])
                print symbol, zrank
                zackranks[symbol] = zrank
        return zackranks
        
    '''
    Brokerage Recommendations

    Today	1 Week Ago	1 Month Ago	2 Months Ago	3 Months Ago
    Strong Buy	22	22	22	22	22
    Buy	4	4	4	4	5
    Hold	6	6	6	6	6
    Sell	0	0	0	0	0
    Strong Sell	0	0	0	0	0
    ABR	1.50	1.50	1.50	1.50	1.52
    '''        
    def getBrokerRecom(self, symbol):
        url = "http://www.zacks.com/stock/research/" + symbol + "/brokerage-recommendations"
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)

        magntable = soup.find("section", {'id':'quote_brokerage_recomm'})
        tdLst = magntable.findAll('td')
        #print tdLst
        abr = {}
        tdlen = len(tdLst)
        idAbrLst = {'abrt':-5,'abr1w':-4,'abr1m':-3,'abr2m':-2,'abr3m':-1}
       
        for key in idAbrLst:
            abr[key] = float(tdLst[idAbrLst[key]].string)
        print abr
        
        
    def getEstimate(self, symbol):
        url = "http://www.zacks.com/stock/quote/" + symbol + "/detailed-estimates"
        page = urllib2.urlopen(url).read()
        soup = BeautifulSoup(page)
        #print page
        magntable = soup.find("section", {'id':'magnitude_estimate'})
        tdLst = magntable.findAll('td')
        cqEstm = []
        nqEstm = []
        tdlen = len(tdLst)
        '''
        [<td class="alpha">Current</td>, <td>0.51</td>, <td>0.56</td>, <td>2.40</td>, <td>2.59</td>, 
        <td class="alpha">7 Days Ago</td>, <td>0.51</td>, <td>0.56</td>, <td>2.40</td>, <td>2.59</td>, 
        <td class="alpha">30 Days Ago</td>, <td>0.51</td>, <td>0.56</td>, <td>2.40</td>, <td>2.59</td>, 
        <td class="alpha">60 Days Ago</td>, <td>0.52</td>, <td>0.56</td>, <td>2.38</td>, <td>2.53</td>, 
        <td class="alpha">90 Days Ago</td>, <td>0.52</td>, <td>0.56</td>, <td>2.39</td>, <td>2.54</td>]

        '''
        idcqLst = [1,6,11,16,21]
        idnqLst = [2,7,12,17,22]
        
        for id in idcqLst:
            if id < tdlen:
                cqEstm.append(tdLst[id].string)
        for id in idnqLst:
            if id < tdlen:
                cqEstm.append(tdLst[id].string)
        
        
        
    '''    
    def write2File(self,zackranks):
        fileName=self.outputpath + "zackrank_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        fp = open(fileName,'w',-1)
        fp.writelines(["%s,%d\n" % (item,zackranks[item])  for item in zackranks])
        fp.close()
    '''

    def test(self):
        #txt= '<div class="zr_rankbox">\n<p>Zacks Rank : 2-Buy <sup class=xxx\nmmk\n'
        txt = 'Zacks Rank : NA <sup class=xxx\nmmk'
        an = re.match(self.pattern,txt)
        if an!=None:
            str1=an.group(1)
            print str1
        print an
          
    def process(self):
        self.parseOption()          
        self.getRank()
        print "Done,exit..."

################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    zr = ZackRank()
    #zr.getEstimate('intc')
    zr.getBrokerRecom('intc')
    #process(sys.argv[1:],None)



