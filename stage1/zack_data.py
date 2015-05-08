'''
run zack_data.py -f symbollist.txt -t starttick -u update_tick_list -r zack_result_csvfile"
'''


import urllib2
import re
import csv
import pandas
import getopt
import sys
import datetime
import marketdata

from bs4 import BeautifulSoup
from collections import OrderedDict


class zack_data:
    def __init__(self):
        #self.rankPattern = '[\d\D]*Zacks.*Rank[/s]*: (.*) <sup class=[\d\D]*'
        #self.rankPattern = '[\d\D]*Zacks.*Rank[/s]*: (.*)[\n]*<sup class=[\d\D]*'
        #<p>Zacks Rank : 2-Buy <sup class="  AAPL
        #self.rankPattern = '[\d\D]*Zacks[\D]*Rank[/s]*: (.)[\d\D]*'

        self.rankPattern = '[\d\D]*Zacks[\D]*Rank[\s]?: (.)[\d\D]*'
        self.cqestCol = ['cq0','cq7','cq30','cq60','cq90']
        
        self.columns = ['rank','indurank','indutotal','etf','abrt','abr1w','abr1m','abr2m',\
            'abr3m','numbr'] + self.cqestCol
            
        
        self.fileName = "./marketdata.csv"
        self.outputfn = "./msdata_zack_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv' 
        self.zackfile = ""
        self.starttick = ""
        self.tickdf = pandas.DataFrame()            
        self.mtd = marketdata.MarketData()
        

        
    def usage(self):
        print "program -f <portfolio_file> -t 'aapl msft' "
        print "example:run zackrank.py -t aapl"
        print "example:run zackrank.py -p portfolio.txt"

    '''    
    def getRank(self,ticklist):
        zackranks = {}
        for symbol in ticklist:
            url = "http://www.zacks.com/stock/quote/"+symbol
            htmltxt =urllib2.urlopen(url).read()
            an = re.match(self.rankPattern, htmltxt)
            if an!=None:
                str1=an.group(1)
                if str1=='N':
                    zrank = 0
                else:
                    zrank = int(str1[0])
                print symbol, zrank
                zackranks[symbol] = zrank
        return zackranks
    ''' 
    def getSymbolRank(self,symbol):
        zrank = -1
        url = "http://www.zacks.com/stock/quote/"+symbol
        try:            
            htmltxt =urllib2.urlopen(url).read()
        except:
            print symbol," Not found"
            return zrank
        an = re.match(self.rankPattern, htmltxt)
        if an!=None:
            str1=an.group(1)
            if str1=='N':
                zrank = 0
            else:
                zrank = int(str1[0])
        print symbol, zrank    
        return zrank

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
    #return 'indurank','indutotal','etf','abrt','abr1w','abr1m','abr2m','abr3m'
    # can combine with rank
    def getBrokerRecom(self, symbol):
        #http://www.zacks.com/stock/research/aapl/brokerage-recommendations
        url = "http://www.zacks.com/stock/research/" + symbol + "/brokerage-recommendations"
        abr = {}
        abr['etf'] = "0"
        try:            
            page = urllib2.urlopen(url).read()
        except:
            print symbol," ABR Not found"
            return abr
   
        soup = BeautifulSoup(page)
        #is ETF?
        isetf = soup.find("sup",attrs={'title':"Zacks ETF Rank Explained"})
        if isetf!=None:
            abr['etf'] = "1"
        else:
            magntable = soup.find("section", {'id':'quote_brokerage_recomm'})
            tdLst = magntable.findAll('td')
    
            tdlen = len(tdLst)
            idAbrLst = {'abrt':-5,'abr1w':-4,'abr1m':-3,'abr2m':-2,'abr3m':-1}
        
            for key in idAbrLst:
                abr[key] = tdLst[idAbrLst[key]].string
            #industry rank by abr
            irba = soup.find("td",attrs={'class':"alpha"},text="Industry Rank by ABR") 
            irbatxt = irba.nextSibling.nextSibling.string
            pattern = "([\d]+)[\s]*of[\s]*([\d]+)"
            an = re.match(pattern,irbatxt)
            indurank = ""
            indutotal = ""
            try:
                if an!=None:
                    indurank = an.group(1)
                    indutotal = an.group(2)
            except:
                pass                
            abr['indurank'] = indurank
            abr['indutotal'] = indutotal
            
            '''
            <td class="alpha"># of Recs in ABR</td>
            <td><span>1</span></td>            
            '''
            nrabr = soup.find("td",attrs={'class':"alpha"},text="# of Recs in ABR") 
            nrabrtxt = ""
            if nrabr!=None:
                nrabrtxt = nrabr.nextSibling.nextSibling.string
            abr['numbr'] = nrabrtxt

        print symbol,abr
        return abr
        
    def parseRank(self,htmltxt):
        an = re.match(self.rankPattern, htmltxt)
        if an!=None:
            str1=an.group(1)
            if str1=='N':
                zrank = "0"
            else:
                zrank = str1[0]
        else:
            zrank = "-1"
        return zrank    

          
    def getEstimate(self, symbol):
        url = "http://www.zacks.com/stock/quote/" + symbol + "/detailed-estimates"
        page = urllib2.urlopen(url).read()
        
        soup = BeautifulSoup(page)
        #print page
        epsEstmDct = {}
        epsEstmDct['rank'] = self.parseRank(page)
        magntable = soup.find("section", {'id':'magnitude_estimate'})
        if magntable!=None:
            tdLst = magntable.findAll('td')
        else:
            return None

        tdlen = len(tdLst)
        '''
        [<td class="alpha">Current</td>, <td>0.51</td>, <td>0.56</td>, <td>2.40</td>, <td>2.59</td>, 
        <td class="alpha">7 Days Ago</td>, <td>0.51</td>, <td>0.56</td>, <td>2.40</td>, <td>2.59</td>, 
        <td class="alpha">30 Days Ago</td>, <td>0.51</td>, <td>0.56</td>, <td>2.40</td>, <td>2.59</td>, 
        <td class="alpha">60 Days Ago</td>, <td>0.52</td>, <td>0.56</td>, <td>2.38</td>, <td>2.53</td>, 
        <td class="alpha">90 Days Ago</td>, <td>0.52</td>, <td>0.56</td>, <td>2.39</td>, <td>2.54</td>]

        '''
        idcqLst = [1,6,11,16,21]
        # idnqLst = [2,7,12,17,22] # next qtr estimate


        for index,theid in enumerate(idcqLst):
            if theid < tdlen:
                epsEstmDct[self.cqestCol[index]] = tdLst[theid].string
        '''        
        for idx in idnqLst:
            if idx < tdlen:
                epsEstmDct[self.cqestCol[idx]] = tdLst[idx].string
        '''
        return epsEstmDct
    
    '''
    main routine
    get past all Quarters earning data from reuter
    '''    
    def getZackData(self,symbol):
        dct = {}
        estdct = self.getEstimate(symbol)
        if estdct!=None:
            dct.update(estdct)
        print dct
        return dct
                
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:u:r:", ["filename", "start","ticklist","zackfile"])
        except getopt.GetoptError:
            print "parameter error"
            sys.exit()
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.fileName = arg
            elif opt in ("-t", "--start"):
                self.starttick = arg
            elif opt in ("-u","--ticklist"):
                items = arg.split(",") #update ticklist only 
                tdict = {}
                for t in items:
                    tick,exg = t.split(".")
                    tdict[tick.upper()] = exg.upper()
                self.tickdf = pandas.DataFrame(list(tdict.iteritems()),columns=['symbol','exg'])
            elif opt in ("-r","--zackfile"):
                self.zackfile = arg
            
        print "symbolfile=",self.fileName
        print "ticklist==="
        if not self.tickdf.empty:
            print self.tickdf
        print "zackfile=",self.zackfile
        return
  
      #load zack csv file
    def loadZackCsvFile(self,fileName):
        print  "Loading zack csv file..."
         
        allLst = {}
        for key in self.columns:
            lst = []
            allLst[key] = lst
        print "number of columns =",len(allLst) 
        table = pandas.DataFrame(allLst,columns=self.columns)
        
        fp = open(fileName,'r',-1)
        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            for rowid, item in enumerate(row):            
                lst = allLst[self.columns[rowid]]
                if rowid>0:
                    item=item.replace(" ","")
                    lst.append(self.mtd.tofloat(item))
                else:
                    lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=self.columns)
        return table
        
    def verifyCol(self,dct):
        missLst = []
        if 'cq0' not in dct:
            missLst.append("Current Qtr Est.")
        if len(missLst)>0:
            print "Missing list:",missLst
            
    # update tick list    
    def updateTickLst(self,zackFile,tickdf): 
        if zackFile!="":
            zackTable = self.loadZackCsvFile(zackFile)
        else:
            zackTable = tickdf
            
        if tickdf.empty:
            if not zackTable.empty:
                tickdf =  zackTable
            else:
                print "both reuterFile and tickdf are empty,exit"
                return
           
        updatelst = tickdf['symbol']
        lenticklst = len(tickdf.index)    
        lf =  zackTable[~zackTable['symbol'].isin(updatelst)]

        #to update table
        allLst = {}
        allCol = ['symbol','exg'] + self.columns
        for key in allCol:
            lst = []
            allLst[key] = lst
        #print "len of allLst",len(allLst)                 
        print "total",lenticklst,"ticks to be updated",len(lf.index),"to keep unchanged"

        if lenticklst>100: 
            outputfn = self.outputfn+"_bak"
            outputfp = open(outputfn,'w',-1)         
            header = 'symbol,exg,' + ', '.join(self.columns) + "\n"
            outputfp.write(header)
       
       
        for index, row in tickdf.iterrows():
            #rowLst = []
            print "downloading ",index,row['symbol'],row['exg']
            rowdct = self.getZackData(row['symbol'])
            line = row['symbol'] + ',' + row['exg']
            if len(rowdct)>0:
                self.verifyCol(rowdct)  
                for key in self.columns:
                    lst = allLst[key]
                    if key in rowdct:
                        lst.append(rowdct[key])
                        line = line + "," + rowdct[key]
                    else:
                        lst.append("")   
                        line = line + "," + ""
                                     
                allLst['symbol'].append(row['symbol'])
                allLst['exg'].append(row['exg'])
                #write to disk is ticks length > 100
                if lenticklst>100:                 
                    line = line + "\n"
                    outputfp.write(line)
                    if index%10 == 0:
                        outputfp.flush()
                                    
            else:
                print "No financials information,skip ",row['symbol'],row['exg']
        
        if lenticklst>100:
            outputfp.close()
        rf = pandas.DataFrame(allLst,columns = allCol)
        mf = lf.append(rf)
        mf.to_csv(self.outputfn,sep=',',index=False)

      
    # update tick data    
    def updateData(self): 
        if self.zackfile!="":
            self.updateTickLst(self.zackfile,self.tickdf)
        else:
            if self.tickdf.empty:
                symbolTable = self.mtd.loadSymbolLstFile(self.fileName)
                self.tickdf = symbolTable[symbolTable['rank']>0]
                self.updateTickLst("",self.tickdf)
            else:
                self.updateTickLst("",self.tickdf)
    '''    
    def write2File(self,zackranks):
        fileName=self.outputpath + "zackrank_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        fp = open(fileName,'w',-1)
        fp.writelines(["%s,%d\n" % (item,zackranks[item])  for item in zackranks])
        fp.close()
    '''
    '''
    def test(self):
        #txt= '<div class="zr_rankbox">\n<p>Zacks Rank : 2-Buy <sup class=xxx\nmmk\n'
        #pattern = '[\d\D]*Zacks[ETF|\s]?Rank[\s]?: (.)[\d\D]*'
        pattern = '[\d\D]*Zacks[\D]*Rank[\s]?: (.)[\d\D]*'
        #txt = '<p>Zacks Rank : 2-Buy <sup class='
        txt = '<p>Zacks Rank : NA <sup clas'
        #txt = '<p>Zacks Rank : 2-Buy <sup class='
        #txt = 'Zacks ETF Rank: 2 - Buy'
        an = re.match(pattern,txt)
        if an!=None:
            str1=an.group(1)
            print str1
        print an
        
    def testRank(self):
        self.getSymbolRank('QQQ')   # 2 ETF
        self.getSymbolRank('AAPL')  # 2 Buy
        self.getSymbolRank('HUSA')  # 0 NR
        self.getSymbolRank('GNMA')  # 0 NR ETF        
        
    def testAbr(self):
        print self.getBrokerRecom('AAPL')
        print self.getBrokerRecom('spy')
        
    def test(self):
        return
    '''
       
    def process(self):
        self.parseOption()
        self.updateData()
        print "Done,exit..."
        
    '''            
    def process(self,tablein,param):
        ticklist = tablein['symbol']
        col = ['symbol']
        df = self.loadZackCsvFile("msdata_zackabr_2015-01-19.csv")     
        df = self.mtd.evalCriteria(df,param,col)                
        #df1 = df[df['symbol'].isin(ticklist)]
        df1 = pandas.merge(tablein,df,how='inner')
        return df1
    '''
    def needPriceData(self):
        return False
        

  
        
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = zack_data()
    obj.process()
    #zr.getEstimate('intc')
    #zr.getBrokerRecom('intc')
    #zr.getPriceSale('intc')
    #obj.process()



