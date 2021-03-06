import getopt
import datetime
import sys
import csv
import pandas
import ms_config
# evaluation criteria on the fly
from collections import OrderedDict
import re

class MarketData:
    def __init__(self):
        '''
        pandas.set_option('display.max_columns', 50)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        pandas.set_option('display.max_rows', 1500)
        '''
        #pandas.set_option('display.max_columns', 50)
        #pandas.set_option('display.precision', 3)
        #pandas.set_option('display.expand_frame_repr', False)
        
        #self.columns = ['symbol','5d','10d','20d', '50d', '100d','200d','max','px', \
        #                'sma10','sma50','sma200','sma10%','sma50%','sma200%']
        #self.perftable = pandas.DataFrame(columns=self.columns) 
        #self.outputpath = "../result/"        
        
        #pandas.options.display.float_format = '{:,.2f}%'.format
        #self.spdretf = {'Consumer Discretionary':'XLY','Consumer Staples':'XLP','Energy':'XLE',\
        #            'Financials':'XLF','Health Care':'XLV','Industrials':'XLI','Materials':'XLB',\
        #            'Technology':'XLK','Utilities':'XLU'}
        #TODO            
        #self.sectormapping = {'Consumer Discretionary':'Consumer Services','Consumer Staples':'Consumer Non-Durables',\
        #        'Energy':'Energy','Financials':'Finance','Health Care':'Health Care','Technology':'Technology',\
        #        'Industrials':'Basic Industries','Industrials':'Transportation','Industrials':'Capital Goods',\
        #        'Materials':'Basic Industries','Capital Goods':'xlb','Health Care':'xlv','Consumer Services':'xly', \
        #        'Utilities':'Public Utilities'}              

        self.cfg = ms_config.MsDataCfg("")
        self.symbol_list_file = self.cfg.getDataConfig("marketdata")
        self.lrlst = pandas.Series()
        self.symbol_col_lst = ['symbol', 'sina', 'goog', 'googexg', 'exg']
        # self.dflr = pandas.DataFrame({}, columns=['symbol', 'exg', 'sina', 'goog', 'googexg'])  # last result df
        # self.dfall = self.dflr
        return


    #aapl#o,msft#o...
    def parseTickLst(self,line):
        items = line.split(",") #update ticklist only 
        tdict = {}
        for t in items:
            td = t.split("#") #delimiter for exchange
            tick = td[0]
            if len(td)>1:
                exg = td[1]
            else:
                exg = ""                    
            tdict[tick.upper()] = exg.upper()
        return tdict
        
    #return dataframe
    def parseTickLstDf(self,line):
        tdict = self.parseTickLst(line)        
        df = pandas.DataFrame(list(tdict.iteritems()),columns=['symbol','exg'])
        lst=['']*len(tdict)
        df['sina']=lst
        df['goog']=tdict.keys()
        df['googexg']=lst
        return df



      
    #google style portfolio file
    #???  
    def parseGooglePortfolio(self,line):
        stocklist = {}
        for item in line.split():      
            symbols = item.split(':')
            exg = ""
            if (len(symbols))>1:
                symbol = symbols[1]
                if symbols[0] == "NYSE":
                    exg = "N"
                elif symbols[0] == "NYSEMKT":                
                    exg = "A" #AMEX
                elif symbols[0] == "NASDAQ":
                    exg = "O" #NASDAQ
            else:
                symbol = symbols[0]                          
            stocklist[symbol] = exg
        return stocklist
    #return dict
    def loadPortfolioFile(self,fn):
        fp = open(fn,'r',-1)
        stocklist={}
        for line in fp:
            if line=="":
                continue
            else:
                stocklist.update(self.parseGooglePortfolio(line))
        fp.close()   
        tickdf = pandas.DataFrame(list(stocklist.iteritems()),columns=['symbol','exg'])           
        return tickdf
 
    # load the marketdata.csv   
    def loadSymbolLstFile(self, fileName):
        #symbol,rank,name,sector,industry,pid,exg,
        fp = open(fileName,'r',-1)
        symbolLst = []
        rankLst = []
        nameLst = []
        sectorLst = []
        industryLst = []
        pidLst = []
        exgLst = []
        reuter = []
        zack = []
        sina = []
        goog = []
        googexg = []
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        try:
            for row in reader:
                if idx==0:
                    idx += 1
                    continue
                symbolLst.append(row[0])
                rankLst.append(int(row[1]))
                nameLst.append(row[2])
                sectorLst.append(row[3])
                industryLst.append(row[4])
                pidLst.append(row[5])
                exgLst.append(row[6])
                collen = len(row)
                if collen == 12:
                    reuter.append(row[7])
                    zack.append(row[8])
                    sina.append(row[9])
                    if (row[10]==""):
                        goog.append(row[0])
                    else:                        
                        goog.append(row[10])
                    googexg.append(row[11])
                else:
                    reuter.append("")
                    zack.append("")
                    sina.append("")
                    goog.append("")
                    googexg.append("")

                idx += 1
        except:
            print "error when reading symbol list file, exit..."
            sys.exit()
        fp.close()      # closing
        table = pandas.DataFrame({'symbol':symbolLst,'rank':rankLst,'name':nameLst,\
            'sector':sectorLst,'industry':industryLst,'pid':pidLst,'exg':exgLst,\
            'reuter':reuter,'zack':zack,'sina':sina,'goog':goog,'googexg':googexg},\
            columns=['symbol','rank','name','sector','industry','pid','exg','reuter',\
            'zack','sina','goog','googexg'])
        return table

    def tofloat(self,item):
        #print item
        try:
            if item=="N/A" or item=="" or item=="NA":
                return 0
            elif item[-1]=="K":
                return float(item.replace("K",""))*1000
            elif item[-1]=="M":
                return float(item.replace("M",""))*1000000
            elif item[-1]=="B":
                return float(item.replace("B",""))*1000000000
            elif item[-1]=="T":
                return float(item.replace("T",""))*1000000000000
            else:
                return float(item)
        except:
            return item
            
    def isNumber(self,s):
        try:
            n=str(float(s))
            if n == "nan" or n=="inf" or n=="-inf" : return False
        except ValueError:
            try:
                complex(s) # for complex
            except ValueError:
                return False
        return True     
            
    # df is the loaded sysmbol list table
    def getSymbolByPid(self,df,pid):        
        #filter via pid mask
        if pid!=0:
            criterion = df['pid'].map(lambda x: ((int(x)&pid)>0))
            df1 = df[criterion] 
        else: #all 
            df1 = df
        return df1

    # idlst 1,2 -> mask = 0x3
    def parsePidLst(self,idLst):
        allMask = 0
        for idstr in idLst:
            theid = int(idstr)
            if theid!=0:
                allMask |= 2**(theid-1)
        return allMask
        
  
      
    #version2
    #colsin - column to display
    #param a dict,key is criteria string
    def evalCriteria(self, df, param, colsin):
        criteria = []
        outputcol = []
        coldict = OrderedDict() #this is output columns
        allcols = df.columns.values
        #for op in param:
        #    criteria.append(op)
        criteria = param.keys()
        #print "criteria",criteria
        #criteria ['dmi_buy<20']

        if not criteria:
            print "criteria is empty,...return original table"
            return df,allcols # TODO
            
        # create output column list and ensure they are unique in this list
        for colnm in colsin:
            coldict[colnm] = 0
            
        # filter by dynamic criteria string
        crstr = ""
        pattern1 = "([a-z][a-z0-9-_]*)"
        pattern2 = "[></]"
        #pattern1 = "([\w]+)([><])([-+]?[0-9]*\.?[0-9]+)"  #cppettm < 20.00 (float)
        #pattern2 = "([\d\D]+)([><])([^[A-Za-z0-9_]+$])"  #saleqtr0 > saleqtr1
        #pattern3 = "([a-z][a-z0-9-]*)" # select column only

        for cr in criteria:
            collst = re.findall(pattern1,cr)
            ration = re.findall(pattern2,cr)
            if len(ration)!=0:
                cr0 = re.sub(pattern1,r"df['\1']",cr)
                if crstr=="":
                    crstr = crstr + "(" + cr0 + ") "
                else:
                    crstr = crstr + "& (" + cr0 + ") "
            # extract column from criteria, then add column for display
            # e.g. only 'dmi_buy', not dmi_sell -> TODO see how to do this later
            for col in collst:
                if col in allcols: #skip parameter which is not column name
                    coldict[col] = 1  #enable the col output
                
                                                        
        #crstr += "(1)"
        print "\tto evaluate criteria(logical) = ", crstr
        outputcol = coldict.keys()
        filteredCols = []
        # get enable columns only list
        for col in coldict:
            if (coldict[col]==1):
                filteredCols.append(col)
                
        if crstr == "":
            df = df[outputcol]
        else:            
            df = df[eval(crstr)][outputcol]
        #print df
        return df,filteredCols

    def adjClosePrice(self, df):
        error1 = 1.05
        error2 = 0.95
        for index, row in df.iterrows():
            adjc = row['Adj Close']
            cl = row['Close']
            ratio = adjc/cl
            if (ratio>error1 or ratio<error2):                
                df.loc[index,'High'] = row['High']*ratio
                df.loc[index,'Low'] = row['Low']*ratio
                df.loc[index,'Open'] = row['Open']*ratio
                df.loc[index,'Close'] = row['Close']*ratio                
        return df
                
    def saveTable(self,df1,path):
        try:
            df1.to_csv(path,sep=',',index=False)
        except:
            print "exception when write to csv ",path
            
        print "Finish wrote to ",path

    # get symbol df from file
    def get_symbol_df(self, app_param):
        df = self.loadSymbolLstFile(app_param.symbol_lst_file)
        dfall = df[self.symbol_col_lst]

        if app_param.ulr:
            if not self.lrlst.empty:
                retdf = dfall[(dfall['symbol'].isin(self.lrlst))]
                retdf = retdf[self.symbol_col_lst]
                return retdf

        if app_param.tick_df.empty:
            if app_param.verbose > 0:
                print "loading from symbol list file..."
            # df = self.loadSymbolLstFile(app_param.symbol_lst_file)
            # self.dfall = df[['symbol', 'sina', 'goog', 'googexg']]
            df = self.getSymbolByPid(df, app_param.pid)[['symbol', 'sina', 'goog', 'googexg']]
        else:
            if app_param.verbose > 0:
                print "using tick list from command line..."
            df = app_param.tick_df

        return df

    def save_last_result_df(self, dflr):
        self.lrlst = dflr['symbol']
        pass

