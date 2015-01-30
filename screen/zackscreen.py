#import zackrank
import sys
import getopt
import datetime
import fundata
import csv
import pandas
import reuterfunda
import marketdata

class ZackScreen:
    def __init__(self):
        self.mkt = marketdata.MarketData()
        self.funda = fundata.FundaData()
        self.reuter = reuterfunda.ReuterFunda()
        self.outputpath = "../result/"
        self.symtable = pandas.DataFrame()
        self.fundafile = ""
        self.zackfile = ""
        self.reuterfile = ""
        self.screen = ""
        self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        #pandas.set_option('display.height', 1500)
        pandas.set_option('display.max_rows', 1500)
        return
    def usage(self):
        print "program -z zackfile -f fundafile -e enddate -r reuterfile -s screenname"
        print "=== QoQ earning increase screen ================================"
        print "run zackscreen.py -f ../data/fundaupdate_2015-01-27.csv -r ../data/reuterfunda_2015-01-27.csv -s er"
        
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:z:r:e:m:s:", ["fundafile", "zackfile","reuterfile","marketdatafile","enddate","screen"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-z", "--zackfile"):
                self.zackfile = arg
            elif opt in ("-f", "--fundafile"):
                self.fundafile = arg
            elif opt in ("-r", "--reuterfile"):
                self.reuterfile = arg
            elif opt in ("-m", "--marketdatafile"):
                self.mktfile = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
            elif opt in ("-s", "--screen"):
                self.screen = arg
                
        if (self.zackfile=="" and self.fundafile=="" and self.reuterfile=="" and self.mktfile==""):
            self.usage()
            sys.exit()
        return
           
    # ABR update file
    # symbol,rank,indurank,indutotal,etf,abrt,abr1w,abr1m,abr2m,abr3m,numbr
    # to use marketdata loadsymbollist()
    def loadSymbolLstFile(self,fileName):
        fp = open(fileName,'r',-1)
        header=[]
        #header = 'symbol,rank,indurank,indutotal,etf,abrt,abr1w,abr1m,abr2m,abr3m,numbr\n'
        reader = csv.reader(fp)  # creates the reader object
        symbolLst=[]
        rankLst=[]
        indurankLst=[]
        indutotalLst=[]
        eftLst=[]
        abrtLst=[]
        abr1wLst=[]
        abr1mLst=[]
        abr2mLst=[]
        abr3mLst=[]
        numbrLst=[]

        idx = 0
        for row in reader:
            if idx == 0:
                header = row
            else:
                symbolLst.append(row[0])
                rankLst.append(int(row[1]))
                indurankLst.append(row[2])
                indutotalLst.append(row[3])
                eftLst.append(row[4])
                #print row[0],row[5]
                if row[5]=="" or row[5]=="NA":
                    abrtLst.append(0)
                else:
                    abrtLst.append(float(row[5]))
                abr1wLst.append(row[6])
                abr1mLst.append(row[7])
                abr2mLst.append(row[8])
                abr3mLst.append(row[9])
                numbrLst.append(row[10])
            idx += 1            
        fp.close() 
        #load into pandas data frame
        return pandas.DataFrame({'symbol':symbolLst,'rank':rankLst,\
            'industry_rank':indurankLst,'industry_total':indutotalLst,'etf':eftLst,\
            'abr_today':abrtLst,'abr_1week':abr1wLst,'abr_1month':abr1mLst,\
            'abr_2month':abr2mLst,'abr_3month':abr3mLst,'num_of_br':numbrLst},\
            columns=['symbol','rank','industry_rank','industry_total','etf','abr_today',\
            'abr_1week','abr_1month','abr_2month','abr_3month','num_of_br'])
     
        
    '''
    def loadFundaFile(self,fileName):
        # symbol,pricesale
        fp = open(fileName,'r',-1)
        psLst={}
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            if row[1]=="N/A":
                ps = 0
            else:
                ps = float(row[1])               
            psLst[row[0]] = ps
            idx += 1
        fp.close()      # closing
        return psLst
    '''
    '''
    BMZ screener
    rank <=3
    abr < 2
    p/s < 0.5
    price change 4,12,24 week top 3,10,20
    average 20 day volume > 50000
    bad thing is will select thoes retail store company which has low p/s
    '''
    def screenBMZ(self): 
        df = self.loadSymbolLstFile(self.zackfile)
        df['ps'] = 0.0
        
        psLst = self.loadFundaFile(self.fundafile)
        #print psLst
        for index, row in df.iterrows():
            symbol = row['symbol']
            df.loc[index,'ps'] = psLst[symbol] 
        #print df   
        
        f1 = df[(df['rank']<=3) & (df['rank']>0) & (df['abr_today'] < 2) & \
            (df['abr_today'] > 0) & (df['ps'] < 0.5) & (df['ps'] > 0)]
        
        f1['p4w'] = 0.0
        f1['p12w'] = 0.0
        f1['p24w'] = 0.0
        f1['vol20'] = 0.0
        for index, row in f1.iterrows():
            symbol = row['symbol']
            ret = self.funda.getPerf(symbol, self.enddate)
            print symbol,ret
            f1.loc[index,'p4w'] = ret['p4w']
            f1.loc[index,'p12w'] = ret['p12w']
            f1.loc[index,'p24w'] = ret['p24w']
            f1.loc[index,'vol20'] = ret['vol20']
        
        f1 = f1[(f1['vol20'] > 50000)]
        print f1
        #meet top3-4week,top10-12week,top20-24week together
        top4w = f1.sort_index(by='p4w',ascending=False).head(3)['symbol']
        top12w = f1.sort_index(by='p12w',ascending=False).head(10)['symbol']
        top24w = f1.sort_index(by='p24w',ascending=False).head(24)['symbol']
        
        bmz1 = f1[(f1['symbol'].isin(top4w)) & (f1['symbol'].isin(top12w)) & (f1['symbol'].isin(top24w))]
        bmz2 = f1.sort_index(by='p24w',ascending=False).head(24).sort_index(by='p12w',ascending=False).head(10).sort_index(by='p4w',ascending=False).head(3)
        #print bmz1,bmz2
                
        
        bmzFn1 = self.outputpath + 'bmz1_'+ self.enddate + '.csv'
        bmzFn2 = self.outputpath + 'bmz2_'+ self.enddate + '.csv'
        try:
            bmz1.to_csv(bmzFn1,sep=',',index=False)
            bmz2.to_csv(bmzFn2,sep=',',index=False)
        except:
            print "exception when write to csv ",bmzFn1,bmzFn2
        
        
    def getTime(self):
        return datetime.datetime.now()

            
    def scrEarningAcc(self):
        startTime = self.getTime()
        df = self.reuter.loadReuterCsvFile(self.reuterfile)
        af = self.funda.loadFundaCsv(self.fundafile)
        sf = self.mkt.loadSymbolLstFile(self.mktfile)
        rf = pandas.merge(sf,df)
        mf = pandas.merge(rf,af)
        
        # epsq increase for constructive 3 qtr,marketcap> 2B,avgvol > 500k
        f0 = mf[ (mf['epsqtr0']>mf['epsqtr-4']) & (mf['epsqtr-1']>mf['epsqtr-5']) \
            & (mf['epsqtr-2']>mf['epsqtr-6']) & (mf['epsqtr-4']>0) & (mf['epsqtr-5']>0) \
            &(mf['epsqtr-6'] >0) \
            &(mf['marketcap']>2000000000) & (mf['avgdailyvol']>500000)]
        
        
        
        
        #f1 = self.mkt.perfReport(f0,outputcol)
        f1 = pandas.DataFrame(f0,index=f0.index,columns=self.mkt.getSymbolLstCol())        
        print f1,len(f1)        
        self.mkt.saveTableFile(f1,"scr_eracc")
        endTime = self.getTime()        
        print "time elapse ",startTime,endTime

        return 
        
    def getZackRank(self):
        rankdict = self.zack.getRank(self.ticklist)
        if len(rankdict) > 1:
            fileName = self.outputpath + "zackrank_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
            fp = open(fileName,'w',-1)
            fp.writelines(["%s,%d\n" % (item, rankdict[item])  for item in rankdict])
            fp.close()
        else:
            print rankdict
        return rankdict
        
    def process(self):
        self.parseOption()
        if self.screen=="":
            self.screenBMZ()
        elif self.screen=="er":
            self.scrEarningAcc()
            
        return
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    zs = ZackScreen()
    zs.process()
