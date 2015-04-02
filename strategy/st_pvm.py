'''
download stock p/s,marketcap,avgvol
'''
import datetime
import pandas

class st_pvm:
    def __init__(self,bt):
        self.columns = ['symbol','pricesale','marketcap','avgdailyvol','px']
        self.colcode = "&f=sp5j1a2l1"
        
        self.cleanup()
        self.stname = "pvm" #strategy name
        #setup component
        #self.tradesup = bt.getTradeSupport()
        #self.simutable = bt.getSimuTable()
        
    def getStrategyName(self):
        return self.stname
    
    # called this when doing automation test
    def cleanup(self):
        self.ind = {}
        self.dl = 0
        return
        
    def getSetupInfoStr(self):
        return self.setupInfo
        
    def setup(self,dl):
        self.cleanup() #must call cleanup before test
        self.dl = dl
        self.setupInfo = "download=%d" % (dl)

    def setupParam(self,param):
        # default parameter
        dl = 0
        if 'download' in param:
            dl = int(param['dl'])
        self.setup(dl)

    #data from yahoo,limit=200               
    def downloadData(self,ticklist):
        symstr = ""
        limit = 199 #yahoo limit is 200
        lenlist = len(ticklist)
        #stockps = []
        dataDct = {}
        dataLst = []
        for idx,col in enumerate(self.columns):
            lst=[]
            dataDct[col]=lst
            dataLst.append(lst)
        
        #retidx= 0 
        for idx, symbol in enumerate(ticklist):
            symstr += symbol
            if idx<(lenlist-1) and (idx%limit!=0):
                symstr +="+"
                
            if idx%limit==0:
                print idx,symstr
                url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
                response = urllib2.urlopen(url)
                cr = csv.reader(response)
                for row in cr:
                    print row
                    for rowid,item in enumerate(row):
                        if rowid==0:
                            dataLst[rowid].append(item) 
                        else:
                            dataLst[rowid].append(self.format(item))
                        
                    #retidx +=1
                symstr=""
                
        if symstr!="":
            print "last get",symstr
            url = "http://finance.yahoo.com/d/quotes.csv?s=" + symstr + self.colcode
            response = urllib2.urlopen(url)
            cr = csv.reader(response)
            for row in cr:
                for rowid,item in enumerate(row):
                    if rowid==0:
                        dataLst[rowid].append(item)
                    else:
                        dataLst[rowid].append(self.format(item))
            
        table=pandas.DataFrame(dataDct,columns=self.columns)
        return table
        return
        
    def algoFunc(self, prices):
        rtd = (prices[-1]/prices[0] - 1)*100
        self.ind['BOS_RTD'] = rtd
        if self.chkdate:
            ckdidx = prices.index.get_loc(self.chkdate)
            ex_ckdidx = ckdidx - 1
            #print "ex chk date",ex_ckdidx
            self.ind['BOS_R0'] = (prices[ex_ckdidx]/prices[0] - 1)*100
            self.ind['BOS_RC'] = (prices[-1]/prices[ckdidx] - 1)*100
            self.ind['BOS_RD'] = self.ind['BOS_RTD'] - self.ind['BOS_R0'] - self.ind['BOS_RC']
        
    def getIndicators(self):
        return self.ind

    # strategy, find the buy&sell signal
    def runStrategy(self,symbol,ohlc,param={}):
        #initialize tradesupport
        self.setupParam(param)

        #self.tradesup.beginTrade(self.setupInfo, symbol, ohlc) 
        #print self.tradesup.getTradeReport()
                
        close_px = ohlc['Adj Close']
        self.algoFunc(close_px)        
        
      
         

  

    def filterOut(self,table,benchStr):
        df = table.loc[table['symbol'] == benchStr]
        #print df
        
        bmrtd = df.loc[0,'BOS_RTD']
        bmr0 = df.loc[0,'BOS_R0']
        bmrc = df.loc[0,'BOS_RC']
        bmrd = df.loc[0,'BOS_RD']
        filterInfo = "Total RTD:%.3f,RT before Check Date:%.3f,RT after Check Date:%.3f,RT on the Check Date:%.3f" \
            % (bmrtd,bmr0,bmrc,bmrd)            
        print filterInfo
        
        filteTable = pandas.DataFrame(columns=table.columns) 
                
        for index, row in table.iterrows():
            symbol = row['symbol']
            srtd = row['BOS_RTD']
            sr0 = row['BOS_R0']
            src = row['BOS_RC']
            srd = row['BOS_RD']
            retRTD = True
            retR0 = True
            retRC = True
            retRD = True
            if self.crtd == 1:
                retRTD = (srtd >= bmrtd)
            if self.cr0 == 1:
                retR0 = (sr0 >= bmr0 )
            if self.crc == 1:
                retRC = (src >= bmrc)
            if self.crd == 1:
                retRD = (srd >= bmrd) 
            if (retRTD and retRTD and retRC and retRD):
                filteTable.loc[len(filteTable)+1]=row                
        
        print filteTable
        return filteTable
   
    # process single date data        
    def procSingleData(self, index, ohlc):
        return
