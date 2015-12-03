'''
zack module, update zack data from website: www.zacks.com
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
import ms_config
from timeit import default_timer as timer
        
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
        self.allcols = ['symbol','exg'] + self.columns
        self.pid = 0

        self.option = ""
        self.tickdf = pandas.DataFrame()            
        self.mtd = marketdata.MarketData()
        self.cfg = ms_config.MsDataCfg()  # default = datafile, cb_config.cfg
        self.mkdataFile=self.cfg.getDataConfig("marketdata") #"./marketdata.csv"
        folder = self.cfg.getDataConfig("cache")
        self.outputfn = folder + "msdata_zack_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv' 


        #self.zackfile = self.cfg.getDataConfig("","zack") #"./marketdata.csv"
        #print self.mkdataFile
        #sys.exit()
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:r:i:h", ["filename", "ticklist","zackfile","pid","merge"])
        except getopt.GetoptError:
            print "parameter error"
            sys.exit()
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.mkdataFile = arg
            #elif opt in ("-t", "--start"):
            #    self.starttick = arg
            elif opt in ("-t","--ticklist"):
                tdict = self.mtd.parseTickLst(arg)
                #print tdict
                self.tickdf = pandas.DataFrame(list(tdict.iteritems()),columns=['symbol','exg'])
                for co in self.columns:
                    self.tickdf[co]=""
                #print self.tickdf
            elif opt in ("-r","--zackfile"):
                self.zackfile = arg
            elif opt in ("-i","--pid"):
                idLst = arg.split(",")
                self.pid = self.mtd.parsePidLst(idLst)
            elif opt in ("-h"):
                self.usage()
                sys.exit()
            elif opt in ("--merge"):
                self.option = "merge" #merge zackfile with others in symbolfile
                
        print "symbolfile=",self.mkdataFile
        print "ticklist==="
        if not self.tickdf.empty:
            print self.tickdf
        #print "zackfile=",self.zackfile
        return
        
    def usage(self):
        print "run zack_data.py -t aapl " #update aapl only
        print "run zack_data.py -r zackfile -t aapl --merge" #merge with zackfile
        print "run zack_data.py -i 1,2,3 "



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
    
    def parseETF(self,soup):
        #is ETF?
        isetf = soup.find("sup",attrs={'title':"Zacks ETF Rank Explained"})
        if isetf!=None:
            self.isEtf = True
            return True
        else:
            self.isEtf = False
            return False
            
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
        
        try:            
            page = urllib2.urlopen(url).read()
        except:
            print "unable to get",symbol,"abr,skip"
            return None
   
        soup = BeautifulSoup(page)
        
        '''
        isetf = self.parseETF(soup)
        if isetf:
            print symbol,"is ETF, skip"
            abr['etf'] = "1"
            return abr
        '''
        
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

        #print symbol,abr
        return abr
        
   
        
    #first try             
    def getEstimate(self, symbol):
        start = timer()
        self.isEtf = False #reset
        url = "http://www.zacks.com/stock/quote/" + symbol + "/detailed-estimates"
        try:
            page = urllib2.urlopen(url).read()
        except:
            print "unable to get",symbol,"estimate,skip"
            return None
        end = timer()
        print "\tget estimate data",(end-start)
        start = timer()
        soup = BeautifulSoup(page)
        epsEstmDct = {}
        isetf = self.parseETF(soup)        
        if isetf:
            print symbol,"is ETF, skip"
            return None
            
        epsEstmDct['rank'] = self.parseRank(page)
        magntable = soup.find("section", {'id':'magnitude_estimate'})
        if magntable==None:
            print "estimation information"
            return epsEstmDct
            
        tdLst = magntable.findAll('td')
        
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
        end = timer()
        print "\tparse estimate data",(end-start)

        return epsEstmDct
    
    '''
    main routine
    get past all Quarters earning data from reuter
    '''    
    def getZackData(self,symbol):
        dct = OrderedDict()
        for key in self.columns:
            dct[key]=""
        #dct['etf']="0"



        estdct = self.getEstimate(symbol)
        if self.isEtf:
            return None

        if estdct!=None:    
            dct.update(estdct)        
        else:
            return None #not proceding further
        start = timer()
        abrdct = self.getBrokerRecom(symbol)
        if abrdct!=None:
            dct.update(abrdct)
        end = timer()    
        print "\tbroker recom",(end-start) 
        return dct
                
   
  
    #load zack csv file
    def loadZackCsvFile(self,fileName):
        print  "Loading zack csv file..."
         
        allLst = {}
        for key in self.allcols:
            lst = []
            allLst[key] = lst
        print "number of columns =",len(allLst) 
        table = pandas.DataFrame(allLst,columns=self.allcols)
        
        fp = open(fileName,'r',-1)
        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            for rowid, item in enumerate(row):            
                lst = allLst[self.allcols[rowid]]
                if rowid>1:
                    item=item.replace(" ","")
                    lst.append(self.mtd.tofloat(item))
                else:
                    lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=self.allcols)
        return table
        
    def verifyCol(self,dct):
        missLst = []
        if 'cq0' not in dct:
            missLst.append("Current Qtr Est.")
        if 'abrt' not in dct:
            missLst.append("Current ABR")
            
        if len(missLst)>0:
            print "Missing list:",missLst            
  
      
    def updateData(self):     
        print "Loading marketdata file",self.mkdataFile
        symbolTable = self.mtd.loadSymbolLstFile(self.mkdataFile)
        df = symbolTable[symbolTable['rank']>0]
        df = self.mtd.getSymbolByPid(df,self.pid)[['symbol','exg']]   
            
        
        if self.tickdf.empty:
            print "update symbolfile pid=",self.pid
            symbolTable = self.mtd.loadSymbolLstFile(self.mkdataFile)
            df = symbolTable[symbolTable['rank']>0]
            df = self.mtd.getSymbolByPid(df,self.pid)[['symbol','exg']]   
            dfup = df[['symbol','exg']]
            for co in self.columns:
                dfup[co]=""
            #dfnc = pandas.DataFrame({},columns=self.allcols)
            #self.updateTickLst(dfnc,dfup)
        else:
            print "update ticklist only"
            dfup = self.tickdf
            #dfnc = pandas.DataFrame({},columns=self.allcols)
            #self.updateTickLst(dfnc,self.tickdf)
      
      ## process the update list
        lenticklst = len(dfup.index)  
        allLst = {}
        allCol = self.allcols
        for key in allCol:
            lst = []
            allLst[key] = lst

        print "total",lenticklst,"ticks to be updated"

        if lenticklst>100: 
            outputfn = self.outputfn+"_bak"
            outputfp = open(outputfn,'w',-1)         
            header = 'symbol,exg,' + ', '.join(self.columns) + "\n"
            outputfp.write(header)
       
        idx = 0
        for index, row in dfup.iterrows():
            print "downloading ",idx,row['symbol'],row['exg']
            idx += 1
            rowdct = self.getZackData(row['symbol'])
            if rowdct==None:
                continue
            #line = row['symbol'] + ',' + row['exg']
            line = ""
            rowdct['symbol'] = row['symbol']
            rowdct['exg'] = row['exg']
            if (len(rowdct)==2):
                print "No zack information",row['symbol'],row['exg']

            self.verifyCol(rowdct)  
            for key in self.allcols:
                lst = allLst[key]
                if key in rowdct:
                    lst.append(rowdct[key])
                    line = line + rowdct[key] + ","
                else:
                    lst.append("")   
                    line = line + "" + ","
                    
            #write to disk is ticks length > 100
            if lenticklst>100:                 
                line = line + "\n"
                outputfp.write(line)
                if idx%10 == 0:
                    outputfp.flush()
                                    

        
        if lenticklst>100:
            outputfp.close()
        
        #delete bak file?        
        mf = pandas.DataFrame(allLst,columns = allCol)        
        print mf
        mf.to_csv(self.outputfn,sep=',',index=False)
        #update dataconfig
        self.cfg.saveDataConfig("zack",self.outputfn)              
         
    def process(self):
        self.parseOption()
        self.updateData()
        print "Done,exit..."
  
        
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



