#import zackrank
import sys
import getopt
import datetime
import fundata
import csv
import pandas

class ZackScreen:
    def __init__(self):
        #self.zack = zackrank.ZackRank()
        self.funda = fundata.FundaData()
        self.outputpath = "../result/"
        self.symtable = pandas.DataFrame()
        self.fundafile = ""
        self.zackfile = ""
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        pandas.set_option('display.height', 1500)
        pandas.set_option('display.max_rows', 1500)
        return
    def usage(self):
        print "program -z zackfile -f fundafile"
        
    def process(self):
        self.parseOption()
        self.screenBMZ()
        return
        
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:z:", ["fundafile", "zackfile"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-z", "--zackfile"):
                self.zackfile = arg
            elif  opt in ("-f", "--fundafile"):
                self.fundafile = arg
                
        if (self.zackfile=="" or self.fundafile==""):
            self.usage()
            sys.exit()
        return
           
    # ABR update file
    # symbol,rank,indurank,indutotal,etf,abrt,abr1w,abr1m,abr2m,abr3m,numbr
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
            'abr_1week','abr_1month','abr_2month','abr_3month'])
     
        
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
    
    #BMZ screener
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
        for index, row in f1.iterrows():
            symbol = row['symbol']
            ret = self.funda.getPerf(symbol)
            print symbol,ret
            f1.loc[index,'p4w'] = ret['p4w']
            f1.loc[index,'p12w'] = ret['p12w']
            f1.loc[index,'p24w'] = ret['p24w']
        
        print f1.sort_index(by='p4w')
        
        bmzFn = self.outputpath + 'bmz_'+ datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'
        try:
            f1.sort_index(by='p24w').to_csv(bmzFn,sep=',')
        except:
            print "exception when write to csv ",bmzFn
            
        
        
        
        
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
    
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    zs = ZackScreen()
    zs.process()
