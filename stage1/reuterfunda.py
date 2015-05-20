# -*- coding: utf-8 -*-
'''
run reuterfunda.py -f symbollist.txt -t starttick -u update_tick_list -r reuter_result_csvfile"
'''

# -*- coding: utf-8 -*-
import urllib2
import re
from bs4 import BeautifulSoup
import pandas
import marketdata
import datetime
import getopt
import sys
import csv


class ReuterFunda:
    def __init__(self):
        pandas.set_option('display.max_columns', 100)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        #pandas.set_option('display.height', 1500)
        pandas.set_option('display.max_rows', 1500)
        self.mtd = marketdata.MarketData()
        self.outputpath = "./"
        self.outputfn = self.outputpath + "msdata_reuter_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv' 
        self.fileName = "./marketdata.csv"
        self.reuterFile = ""
        #self.starttick = ""
        self.option = ""
        self.tickdf = pandas.DataFrame()
        self.columns = [
            'saleqtr0','saleqtr-1','saleqtr-2','saleqtr-3','saleqtr-4','saleqtr-5','saleqtr-6','saleqtr-7',\
            'saleqtr-8','saleqtr-9','epsqtr0','epsqtr-1','epsqtr-2','epsqtr-3','epsqtr-4','epsqtr-5','epsqtr-6',\
            'epsqtr-7','epsqtr-8','epsqtr-9',\
            \
            'numest','saleq1e','saleq1ey','saleq2e','saleq2ey','saley1e','saley1ey','saley2e','saley2ey','epsq1e',\
            'epsq1ey','epsq2e','epsq2ey','epsy1e','epsy1ey','epsy2e','epsy2ey','numltgr','ltgre','ltgrey',\
            \
            'cppettm','indupettm','sectorpettm','cppehigh5y','indupehigh5y','sectorpehigh5y','cppelow5y','indupelow5y',\
            'sectorpelow5y','cpbeta','indubeta','sectorbeta','cppsttm','indupsttm','sectorpsttm','cppbmrq','indupbmrq',\
            'sectorpbmrq','cppcfttm','indupcfttm','sectorpcfttm','cppfcfttm','indupfcfttm','sectorpfcfttm',\
            \
            'divyield','div5y','div5ygr','payoutratio',\
            \
            'cpsalemrqyoy','indusalemrqyoy','sectorsalemrqyoy','cppsalettmyoy','indusalettmyoy','sectorsalettmyoy','cpsale5ygr',\
            'indusale5ygr','sectorsale5ygr','cpepsmrqyoy','induepsmrqyoy','sectorepsmrqyoy','cpepsttmyoy','induepsttmyoy',\
            'sectorepsttmyoy','cpeps5ygr','indueps5ygr','sectoreps5ygr','cpcap5ygr','inducap5ygr','sectorcap5ygr',\
            \
            'cpdebt2equity','indudebt2equity','secdebt2equity','cpquira','induquira','secquira','cpcurra','inducura','seccurra',\
            \
            'cpgm','indugm','sectorgm','cpgm5y','indugm5y','sectorgm5y','cpom','induom','sectorom','cpom5y','induom5y','sectorom5y',\
            'cpnm','indunm','sectornm','cpnm5y','indunm5y','sectornm5y',\
            \
            'cproa','induroa','sectorroa','cproa5y','induroa5y','sectorroa5y','cproi','induroi','sectorroi','cproi5y','induroi5y','sectorroi5y','cproe','induroe',\
            'sectorroe','cproe5y','induroe5y','sectorroe5y'
            ]
        self.allcols = ['symbol','exg'] + self.columns
        self.pid = 0
        # base set columns
        self.colbase = ['symbol','cppettm','cppsttm','cppbmrq','cppcfttm',\
                    'divyield','payoutratio',\
                    'cpsalemrqyoy','cppsalettmyoy','cpsale5ygr','cpepsmrqyoy','cpepsttmyoy','cpeps5ygr',\
                    'cpcurra','cpquira','cpdebt2equity',\
                    'cpgm','cpom','cpnm','cpbeta']

    def parseOption(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:i:t:r:hm")
            #,["filename", "pid","ticklist","reuterfile","help","merge"]
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
        print opts,args
        for opt, arg in opts:
            if opt in ("-f"):#symbol file
                self.fileName = arg            
            elif opt in ("-i"):
                idLst = arg.split(",")
                self.pid = self.mtd.parsePidLst(idLst)    
            elif opt in ("-t"):
                self.tickdf = self.mtd.parseTickLstDf(arg)                                       
            elif opt in ("-r"):
                self.reuterFile = arg
            elif opt in ("-h"):
                self.usage()
                sys.exit()
            elif opt in ("-m"):
                self.option = "merge" #merge reuterfile with others in symbolfile
     
    
            
        print "symbolfile=",self.fileName
        print "ticklist=="
        if not self.tickdf.empty:
            print self.tickdf
        print "reuterfile=",self.reuterFile
        return           
    '''
    main routine
    get past all Quarters earning data from reuter
    '''    
    def getEarningData(self,symbol):
        #http://www.reuters.com/finance/stocks/financialHighlights?symbol=MSFT.O
        url = "http://www.reuters.com/finance/stocks/financialHighlights?symbol=" + symbol
        fundadct = {}

        try:            
            page = urllib2.urlopen(url).read()
        except:
            print symbol," reuter fundata Not found"
            return fundadct
   
        #symbol found?
        if 'not found' in page:
            print symbol," reuter fundata Not found"
            return fundadct
            
        soup = BeautifulSoup(page)

        #earning past quarter
        dataTableLst = soup.findAll("table",attrs={'class':"dataTable"})
        retmx={'er':0,'estm':0,'vr':0,'div':0,'gr':0,'fins':0,'mrg':0,'me':0}
            
        #retdct = {}
        for table in dataTableLst:
            if retmx['er'] == 0:
                ret=self.parsePastQEarning(table)
                if ret!=None and len(ret)>0:
                    retmx['er'] = 1
                    fundadct.update(ret)
                    continue
            if retmx['estm'] == 0:
                ret=self.parseEstimate(table)
                if ret!=None and len(ret)>0:
                    retmx['estm'] = 1
                    fundadct.update(ret)
                    continue
                
                       
            if retmx['vr'] == 0:
                ret=self.parseValuationRatio(table)
                if ret!=None and len(ret)>0:
                    retmx['vr'] = 1
                    fundadct.update(ret)
                    continue
                    
            if retmx['div'] == 0:
                ret=self.parseDividend(table)
                if ret!=None and len(ret)>0:
                    retmx['div'] = 1
                    fundadct.update(ret)
                    continue
                                                
            if retmx['gr'] == 0:
                ret = self.parseGrowth(table)
                if ret!=None and len(ret)>0:
                    retmx['gr'] = 1
                    fundadct.update(ret)
                    continue
            if retmx['fins'] == 0:
                ret = self.parseFinanStrength(table)
                if ret!=None and len(ret)>0:
                    retmx['fins'] = 1
                    fundadct.update(ret)
                    continue
                     
            if retmx['mrg'] == 0:
                ret=self.parseProfitRatio(table)
                if ret!=None and len(ret)>0:
                    retmx['mrg'] = 1
                    fundadct.update(ret)
                    continue
                                        
            if retmx['me'] == 0:
                ret = self.parseMangEffect(table)
                if ret!=None and len(ret)>0:
                    retmx['me'] = 1
                    fundadct.update(ret)
                    continue
        print "\tparsing is done."                        
        return fundadct
        
    def verifyCol(self,dct):
        missLst = []
        if 'cppettm' not in dct:
            missLst.append("P/E TTM")
        if 'cpdebt2equity' not in dct:
            missLst.append("Total Debt to Equity (MRQ)")
        if 'saleqtr0' not in dct:
            missLst.append("Earning")
        if 'cpgm' not in dct:
            missLst.append("Gross Margin (TTM)")
        if 'saleq1e' not in dct:
            missLst.append("Estimate")
        if len(missLst)>0:
            print "Missing list:",missLst
        
   
        
    #ROA,ROI,ROE
    def parseMangEffect(self,table):
        '''
        txt=table.__str__()
        #print type(txt),txt
        pattern = "[\d\D]*Return on Assets[\d\D]*"
        an = re.match(pattern,txt)
        if an!=None:
            print txt
        '''
        mangeff = {}

        tag = table.find("td",text=re.compile('[\d\D]*Return on Assets \(TTM\)[\d\D]*'))        
        if tag!=None:
            cproatag = tag.nextSibling.nextSibling
            induroatag = cproatag.nextSibling.nextSibling            
            sectorroatag = induroatag.nextSibling.nextSibling
            mangeff['cproa'] = self.tofloat(cproatag.string)
            mangeff['induroa'] = self.tofloat(induroatag.string)
            mangeff['sectorroa'] = self.tofloat(sectorroatag.string)
        else:
            #print "Return on Assets (TTM) not found"
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Assets - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cproatag = tag.nextSibling.nextSibling
            induroatag = cproatag.nextSibling.nextSibling            
            sectorroatag = induroatag.nextSibling.nextSibling
            mangeff['cproa5y'] = self.tofloat(cproatag.string)
            mangeff['induroa5y'] = self.tofloat(induroatag.string)
            mangeff['sectorroa5y'] = self.tofloat(sectorroatag.string)
        else:
            print "Return on Assets - 5 Yr. Avg. not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Investment \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproi'] = self.tofloat(cptag.string)
            mangeff['induroi'] = self.tofloat(indutag.string)
            mangeff['sectorroi'] = self.tofloat(sectortag.string)
        else:
            print "Return on Investment (TTM) not found"
            #return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Return on Investment - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproi5y'] = self.tofloat(cptag.string)
            mangeff['induroi5y'] = self.tofloat(indutag.string)
            mangeff['sectorroi5y'] = self.tofloat(sectortag.string)
        else:
            print "Return on Investment - 5 Yr. Avg. not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Equity \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproe'] = self.tofloat(cptag.string)
            mangeff['induroe'] = self.tofloat(indutag.string)
            mangeff['sectorroe'] = self.tofloat(sectortag.string)
        else:
            print "Return on Equity (TTM) not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Equity - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproe5y'] = self.tofloat(cptag.string)
            mangeff['induroe5y'] = self.tofloat(indutag.string)
            mangeff['sectorroe5y'] = self.tofloat(sectortag.string)
        else:
            print "Return on Equity - 5 Yr. Avg. not found"
            #return None
        
        return mangeff
        
    def parsePastQEarning(self,table):
        revtag = table.find("th",attrs={'class':"data"},text="Revenue*")
        reveps = {}
        #print revtag
        if revtag!=None:
            dataLst = table.findAll("td",attrs={'class':"data"})
            #print dataLst
            if dataLst!=None:
                idx = 0
                for data in dataLst:
                   #txt = data.string.replace(",","")
                   salekey = "saleqtr%d" % -(idx/2)
                   epskey = "epsqtr%d" % -(idx/2)
                   #print idx,data
                   if idx%2 == 0:
                       reveps[salekey] = self.tofloat(data.string)
                   else:
                       reveps[epskey] = self.tofloat(data.string)
                   idx += 1                
                return reveps
            else:
                print "PastQ earning not found"
                return None
        else:
            #print "PastQ earning not found"
            return None

    '''
    GM,operateMargin, and net profit margin
    '''
    def parseProfitRatio(self,table):
        profitratio = {}

        tag = table.find("td",text=re.compile('[\d\D]*Gross Margin \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpgm'] = self.tofloat(cptag.string)
            profitratio['indugm'] = self.tofloat(indutag.string)
            profitratio['sectorgm'] = self.tofloat(sectortag.string)
        else:
            #print "Gross Margin (TTM) not found"
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Gross Margin - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpgm5y'] = self.tofloat(cptag.string)
            profitratio['indugm5y'] = self.tofloat(indutag.string)
            profitratio['sectorgm5y'] = self.tofloat(sectortag.string)
        else:
            print "Gross Margin - 5 Yr. Avg. not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Operating Margin \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpom'] = self.tofloat(cptag.string)
            profitratio['induom'] = self.tofloat(indutag.string)
            profitratio['sectorom'] = self.tofloat(sectortag.string)
        else:
            print "Operating Margin (TTM) not found"
            #return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Operating Margin - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpom5y'] = self.tofloat(cptag.string)
            profitratio['induom5y'] = self.tofloat(indutag.string)
            profitratio['sectorom5y'] = self.tofloat(sectortag.string)
        else:
            print "Operating Margin - 5 Yr. Avg. not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Net Profit Margin \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpnm'] = self.tofloat(cptag.string)
            profitratio['indunm'] = self.tofloat(indutag.string)
            profitratio['sectornm'] = self.tofloat(sectortag.string)
        else:
            print "Net Profit Margin (TTM) not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Net Profit Margin - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpnm5y'] = self.tofloat(cptag.string)
            profitratio['indunm5y'] = self.tofloat(indutag.string)
            profitratio['sectornm5y'] = self.tofloat(sectortag.string)
        else:
            print "Net Profit Margin - 5 Yr. Avg. not found"
            #return None
        
        return profitratio

    def parseValuationRatio(self,table):
        valratio = {}
        tag = table.find("td",text=re.compile('[\d\D]*P/E Ratio \(TTM\)[\d\D]*'))    
        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppettm'] = self.tofloat(cptag.string)
            valratio['indupettm'] = self.tofloat(indutag.string)
            valratio['sectorpettm'] = self.tofloat(sectortag.string)           
        else:
            #print "P/E Ratio (TTM) not found"
            return None
        
        tag = table.find("td",text=re.compile('[\d\D]*P/E High - Last 5 Yrs\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppehigh5y'] = self.tofloat(cptag.string)
            valratio['indupehigh5y'] = self.tofloat(indutag.string)
            valratio['sectorpehigh5y'] = self.tofloat(sectortag.string)
        else:
            print "P/E High - Last 5 Yrs. not found"

      
        tag = table.find("td",text=re.compile('[\d\D]*P/E Low - Last 5 Yrs\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppelow5y'] = self.tofloat(cptag.string)
            valratio['indupelow5y'] = self.tofloat(indutag.string)
            valratio['sectorpelow5y'] = self.tofloat(sectortag.string)
        else:
            print "P/E Low - Last 5 Yrs. not found"

       
        tag = table.find("td",text=re.compile('[\d\D]*Beta[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cpbeta'] = self.tofloat(cptag.string)
            valratio['indubeta'] = self.tofloat(indutag.string)
            valratio['sectorbeta'] = self.tofloat(sectortag.string)
        else:
            print "Beta not found"

            
        tag = table.find("td",text=re.compile('[\d\D]*Price to Sales \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppsttm'] = self.tofloat(cptag.string)
            valratio['indupsttm'] = self.tofloat(indutag.string)
            valratio['sectorpsttm'] = self.tofloat(sectortag.string)
        else:
            print "Beta not found"


        tag = table.find("td",text=re.compile('[\d\D]*Price to Book \(MRQ\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppbmrq'] = self.tofloat(cptag.string)
            valratio['indupbmrq'] = self.tofloat(indutag.string)
            valratio['sectorpbmrq'] = self.tofloat(sectortag.string)
        else:
            print "Price to Book (MRQ) not found"

                      
        tag = table.find("td",text=re.compile('[\d\D]*Price to Cash Flow \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppcfttm'] = self.tofloat(cptag.string)
            valratio['indupcfttm'] = self.tofloat(indutag.string)
            valratio['sectorpcfttm'] = self.tofloat(sectortag.string)
        else:
            print "Price to Cash Flow (TTM) not found"


        tag = table.find("td",text=re.compile('[\d\D]*Price to Free Cash Flow \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppfcfttm'] = self.tofloat(cptag.string)
            valratio['indupfcfttm'] = self.tofloat(indutag.string)
            valratio['sectorpfcfttm'] = self.tofloat(sectortag.string)
        else:
            print "\tPrice to Free Cash Flow (TTM) not found"

        
        
        return valratio    
    
    # growth    
    def parseGrowth(self,table):
        gr = {}
        tag = table.find("td",text=re.compile('[\d\D]*Sales \(MRQ\) vs Qtr\. 1 Yr\. Ago[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpsalemrqyoy'] = self.tofloat(cptag.string)
            gr['indusalemrqyoy'] = self.tofloat(indutag.string)
            gr['sectorsalemrqyoy'] = self.tofloat(sectortag.string)
        else:
            #print "Sales (MRQ) vs Qtr. 1 Yr. Ago not found"
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Sales \(TTM\) vs TTM 1 Yr\. Ago[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cppsalettmyoy'] = self.tofloat(cptag.string)
            gr['indusalettmyoy'] = self.tofloat(indutag.string)
            gr['sectorsalettmyoy'] = self.tofloat(sectortag.string)
        else:
            print "Sales (TTM) vs TTM 1 Yr. Ago not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Sales - 5 Yr\. Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpsale5ygr'] = self.tofloat(cptag.string)
            gr['indusale5ygr'] = self.tofloat(indutag.string)
            gr['sectorsale5ygr'] = self.tofloat(sectortag.string)
        else:
            print "Sales - 5 Yr. Growth Rate not found"
            #return None
            
        tag = table.find("td",text=re.compile('[\d\D]*EPS \(MRQ\) vs Qtr\. 1 Yr\. Ago[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpepsmrqyoy'] = self.tofloat(cptag.string)
            gr['induepsmrqyoy'] = self.tofloat(indutag.string)
            gr['sectorepsmrqyoy'] = self.tofloat(sectortag.string)
        else:
            print "EPS (MRQ) vs Qtr. 1 Yr. Ago not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*EPS \(TTM\) vs TTM 1 Yr\. Ago[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpepsttmyoy'] = self.tofloat(cptag.string)
            gr['induepsttmyoy'] = self.tofloat(indutag.string)
            gr['sectorepsttmyoy'] = self.tofloat(sectortag.string)
        else:
            print "EPS (TTM) vs TTM 1 Yr. Ago not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*EPS - 5 Yr\. Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpeps5ygr'] = self.tofloat(cptag.string)
            gr['indueps5ygr'] = self.tofloat(indutag.string)
            gr['sectoreps5ygr'] = self.tofloat(sectortag.string)
        else:
            print "EPS - 5 Yr. Growth Rate not found"
            #return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Capital Spending - 5 Yr\. Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpcap5ygr'] = self.tofloat(cptag.string)
            gr['inducap5ygr'] = self.tofloat(indutag.string)
            gr['sectorcap5ygr'] = self.tofloat(sectortag.string)
        else:
            print "Capital Spending - 5 Yr. Growth Rate not found"
            #return None
        return gr
     
    #parse sale and eps estimate   
    '''
    #some symbol has q1,q2,y1 only, need to find a new way 
    def parseEstimate(self,table):
        estm = {}
        tag = table.find("th",text=re.compile('[\d\D]*# of Estimates[\d\D]*')) 
        if tag==None:
            return None
        # find all td class='data'
        #print "found estimate"
        idset = {'numest':0,'saleq1e':1,'saleq1ey':4,'saleq2e':6,'saleq2ey':9,'saley1e':11,\
            'saley1ey':14,'saley2e':16,'saley2ey':19,'epsq1e':21,'epsq1ey':24,\
            'epsq2e':26,'epsq2ey':29,'epsy1e':31,'epsy1ey':34,'epsy2e':36,\
            'epsy2ey':39,'ltgre':41,'ltgrey':44} 
            
        dataLst = table.findAll("td",attrs={'class':"data"})
        
        if dataLst!=None:
            print len(dataLst)
            for name in idset:
                print name
                estm[name] = self.tofloat(dataLst[idset[name]].string)
            return estm
        return None
    '''
    def parseEstimate(self,table):
        estm = {}
        tag = table.find("th",text=re.compile('[\d\D]*# of Estimates[\d\D]*')) 
        if tag == None:
            #print "Estimate not found"
            return None
        
        #pattern="[\d\D]*SALES \(in millions\)[\d\D]*?</tr>?([\d\D]*)<tr>[\d\D]*Earnings \(per share\)[\d\D]*?</tr>?([\d\D]*)<tr>[\d\D]*LT Growth Rate[\d\D]*"
        pattern="[\d\D]*SALES \(in millions\)[\d\D]*?</tr>?([\d\D]*)<tr>[\d\D]*Earnings \(per share\)[\d\D]*?</tr>?([\d\D]*)</tbody>[\d\D]*"
        txt = table.__str__()
      
        an = re.match(pattern,txt)
        if an!=None:
            #print an.group(1)
            soup1 = BeautifulSoup(an.group(1))
            tagLst = soup1.findAll("td",text=re.compile('[\d\D]*Quarter Ending[\d\D]*')) 
            for idx,data in enumerate(tagLst):
                key1="saleq%de" % (idx+1)
                key2="saleq%dey" % (idx+1)
                numestmtag = data.nextSibling.nextSibling
                qestm = numestmtag.nextSibling.nextSibling
                qesth = qestm.nextSibling.nextSibling
                qestl = qesth.nextSibling.nextSibling                                                
                qesty = qestl.nextSibling.nextSibling
                estm[key1] = self.tofloat(qestm.string)
                estm[key2] = self.tofloat(qesty.string)
                
                #print qestm.string,qesty.string
            tagLst = soup1.findAll("td",text=re.compile('[\d\D]*Year Ending[\d\D]*')) 
            for idx,data in enumerate(tagLst):
                key1="saley%de" % (idx+1)
                key2="saley%dey" % (idx+1)
                numestmtag = data.nextSibling.nextSibling
                daestm = numestmtag.nextSibling.nextSibling
                daesth = daestm.nextSibling.nextSibling
                daestl = daesth.nextSibling.nextSibling                                                
                daesty = daestl.nextSibling.nextSibling
                estm[key1] = self.tofloat(daestm.string)
                estm[key2] = self.tofloat(daesty.string)
                estm['numest'] = numestmtag.string                 
            #print "=========================================="
            #print an.group(2)
            soup1 = BeautifulSoup(an.group(2))
            tagLst = soup1.findAll("td",text=re.compile('[\d\D]*Quarter Ending[\d\D]*')) 
            for idx,data in enumerate(tagLst):
                key1="epsq%de" % (idx+1)
                key2="epsq%dey" % (idx+1)
                numestmtag = data.nextSibling.nextSibling
                qestm = numestmtag.nextSibling.nextSibling
                qesth = qestm.nextSibling.nextSibling
                qestl = qesth.nextSibling.nextSibling                                                
                qesty = qestl.nextSibling.nextSibling
                estm[key1] = self.tofloat(qestm.string)
                estm[key2] = self.tofloat(qesty.string)
                
            tagLst = soup1.findAll("td",text=re.compile('[\d\D]*Year Ending[\d\D]*')) 
            for idx,data in enumerate(tagLst):
                key1="epsy%de" % (idx+1)
                key2="epsy%dey" % (idx+1)
                numestmtag = data.nextSibling.nextSibling
                daestm = numestmtag.nextSibling.nextSibling
                daesth = daestm.nextSibling.nextSibling
                daestl = daesth.nextSibling.nextSibling                                                
                daesty = daestl.nextSibling.nextSibling
                estm[key1] = self.tofloat(daestm.string)
                estm[key2] = self.tofloat(daesty.string)
                #estm['numest'] = numestmtag.string  
        else:
            print "Estimate not found"
            #return None
            
        tag = table.find("td",text=re.compile('[\d\D]*LT Growth Rate[\d\D]*'))        
        if tag!=None:
            numltgrtag = tag.nextSibling.nextSibling
            ltmtag = numltgrtag.nextSibling.nextSibling            
            lthtag = ltmtag.nextSibling.nextSibling
            ltltag = lthtag.nextSibling.nextSibling
            ltytag = ltltag.nextSibling.nextSibling
            estm['numltgr'] = self.tofloat(numltgrtag.string)
            estm['ltgre'] = self.tofloat(ltmtag.string)
            estm['ltgrey'] = self.tofloat(ltytag.string)
        #else:
        #    print "LT Growth Rate not found"
        #    return None
        # some don't have LT growth rate    
        return estm 
    
    def parseDividend(self, table): 
        div = {}       
        tag = table.find("td",text=re.compile('[\d\D]*Dividend Yield'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            div['divyield'] = self.tofloat(cptag.string)
        else:
            #print "Dividend Yield not found"
            return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Dividend Yield - 5 Year Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            div['div5y'] = self.tofloat(cptag.string)
        else:
            print "\tDividend Yield - 5 Year Avg. not found"
            #return None
        
        tag = table.find("td",text=re.compile('[\d\D]*Dividend 5 Year Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            div['div5ygr'] = self.tofloat(cptag.string)
        else:
            print "Dividend 5 Year Growth Rat not found"
            #return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Payout Ratio\(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            div['payoutratio'] = self.tofloat(cptag.string)
        else:
            print "Payout Ratio(TTM) not found"
            #return None
             
        #print div  
        return div
    
    def parseFinanStrength(self,table):
        fins = {}
        tag = table.find("td",text=re.compile('[\d\D]*Total Debt to Equity \(MRQ\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            fins['cpdebt2equity'] = self.tofloat(cptag.string)
            fins['indudebt2equity'] = self.tofloat(indutag.string)
            fins['secdebt2equity'] = self.tofloat(sectortag.string)
        else:
            return None
        
        tag = table.find("td",text=re.compile('[\d\D]*Quick Ratio \(MRQ\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            fins['cpquira'] = self.tofloat(cptag.string)
            fins['induquira'] = self.tofloat(indutag.string)
            fins['secquira'] = self.tofloat(sectortag.string)
        else:
            print "Quick Ratio (MRQ) not found"
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Current Ratio \(MRQ\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            fins['cpcurra'] = self.tofloat(cptag.string)
            fins['inducura'] = self.tofloat(indutag.string)
            fins['seccurra'] = self.tofloat(sectortag.string)
        else:
            print "Current Ratio (MRQ) not found"
            #return None
            
        return fins
    
    #move to marketdata    
    def tofloat(self,txt):
        if txt=="--" or txt==None:
            return "0"
        else:
            return txt.replace(",","")
            
       
  
        
    def loadReuterCsvFile(self,fileName):
        print "Loading reuter csv file..."
        columns = ['symbol','exg',\
            \
            'saleqtr0','saleqtr-1','saleqtr-2','saleqtr-3','saleqtr-4','saleqtr-5','saleqtr-6','saleqtr-7',\
            'saleqtr-8','saleqtr-9','epsqtr0','epsqtr-1','epsqtr-2','epsqtr-3','epsqtr-4','epsqtr-5','epsqtr-6',\
            'epsqtr-7','epsqtr-8','epsqtr-9',\
            \
            'numest','saleq1e','saleq1ey','saleq2e','saleq2ey','saley1e','saley1ey','saley2e','saley2ey','epsq1e',\
            'epsq1ey','epsq2e','epsq2ey','epsy1e','epsy1ey','epsy2e','epsy2ey','numltgr','ltgre','ltgrey',\
            \
            'cppettm','indupettm','sectorpettm','cppehigh5y','indupehigh5y','sectorpehigh5y','cppelow5y','indupelow5y',\
            'sectorpelow5y','cpbeta','indubeta','sectorbeta','cppsttm','indupsttm','sectorpsttm','cppbmrq','indupbmrq',\
            'sectorpbmrq','cppcfttm','indupcfttm','sectorpcfttm','cppfcfttm','indupfcfttm','sectorpfcfttm',\
            \
            'divyield','div5y','div5ygr','payoutratio',\
            \
            'cpsalemrqyoy','indusalemrqyoy','sectorsalemrqyoy','cppsalettmyoy','indusalettmyoy','sectorsalettmyoy','cpsale5ygr',\
            'indusale5ygr','sectorsale5ygr','cpepsmrqyoy','induepsmrqyoy','sectorepsmrqyoy','cpepsttmyoy','induepsttmyoy',\
            'sectorepsttmyoy','cpeps5ygr','indueps5ygr','sectoreps5ygr','cpcap5ygr','inducap5ygr','sectorcap5ygr',\
            \
            'cpdebt2equity','indudebt2equity','secdebt2equity','cpquira','induquira','secquira','cpcurra','inducura','seccurra',\
            \
            'cpgm','indugm','sectorgm','cpgm5y','indugm5y','sectorgm5y','cpom','induom','sectorom','cpom5y','induom5y','sectorom5y',\
            'cpnm','indunm','sectornm','cpnm5y','indunm5y','sectornm5y',\
            \
            'cproa','induroa','sectorroa','cproa5y','induroa5y','sectorroa5y','cproi','induroi','sectorroi','cproi5y','induroi5y','sectorroi5y','cproe','induroe',\
            'sectorroe','cproe5y','induroe5y','sectorroe5y'
            ]
    
        
        allLst = {}
        for key in columns:
            lst = []
            allLst[key] = lst
        print "len of allLst",len(allLst) 
                
        table = pandas.DataFrame(allLst,columns=columns)
        
        fp = open(fileName,'r',-1)
        
        reader = csv.reader(fp)  # creates the reader object
        idx = 0
        for row in reader:
            if idx==0:
                idx += 1
                continue
            #rowidset = [0,len(row)]
            for rowid, item in enumerate(row):            
                #print rowid
                #print columns[rowid]
                lst = allLst[columns[rowid]]
                if rowid>1:
                    item=item.replace(" ","")
                    if item=="":
                        item=0
                    #print item
                    lst.append(float(item))
                else:
                    lst.append(item)
            idx += 1
        fp.close()        
        
        table = pandas.DataFrame(allLst,columns=columns)
        return table
    
        
    # update tick list    
    def updateTickLst0(self,reuterFile,tickdf): 
        if reuterFile!="":
            reuterTable = self.loadReuterCsvFile(reuterFile)
        else:
            reuterTable = tickdf
            
        if tickdf.empty:
            if not reuterTable.empty:
                tickdf =  reuterTable
            else:
                print "both reuterFile and tickdf are empty,exit"
                return
           
        updatelst = tickdf['symbol']
        lenticklst = len(tickdf.index)    
        lf =  reuterTable[~reuterTable['symbol'].isin(updatelst)]

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
       
        idx = 0
        for index, row in tickdf.iterrows():
            #rowLst = []
            print "downloading ",index,row['symbol'],row['exg']
            rowdct = self.getEarningData(row['symbol']+"."+row['exg'])
            line = row['symbol'] + ',' + row['exg']
            idx += 1
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
                    if idx%10 == 0:
                        outputfp.flush()
                                    
            else:
                print "No financials information,skip ",row['symbol'],row['exg']
        
        if lenticklst>100:
            outputfp.close()
        rf = pandas.DataFrame(allLst,columns = allCol)
        mf = lf.append(rf)
        mf.to_csv(self.outputfn,sep=',',index=False)
          

    def updateTickLst(self,dfnc,dfup): 
        '''
        if reuterFile!="":
            reuterTable = self.loadReuterCsvFile(reuterFile)
        else:
            reuterTable = tickdf
            
        if tickdf.empty:
            if not reuterTable.empty:
                tickdf =  reuterTable
            else:
                print "both reuterFile and tickdf are empty,exit"
                return
        '''
        
        #updatelst = tickdf['symbol']
        lenticklst = len(dfup.index)    
        #lf =  reuterTable[~reuterTable['symbol'].isin(updatelst)]

        #to update table
        allLst = {}
        allCol = self.allcols
        for key in allCol:
            lst = []
            allLst[key] = lst
        #print "len of allLst",len(allLst)                 
        print "total",lenticklst,"ticks to be updated",len(dfnc.index),"to keep unchanged"

        if lenticklst>100: 
            outputfn = self.outputfn+"_bak"
            outputfp = open(outputfn,'w',-1)         
            header = 'symbol,exg,' + ', '.join(self.columns) + "\n"
            outputfp.write(header)
       
        idx = 0
        for index, row in dfup.iterrows():
            #rowLst = []
            print "downloading ",idx,row['symbol'],row['exg']
            idx += 1
            rowdct = self.getEarningData(row['symbol']+"."+row['exg'])
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
        mf = dfnc.append(rf)
        mf.to_csv(self.outputfn,sep=',',index=False)
  

    def updateData(self): 
        if self.reuterFile!="":
            reuterTable = self.loadReuterCsvFile(self.reuterFile)

        if self.reuterFile!="":
            if self.option == "merge":
                reuterList = reuterTable['symbol']
                if self.tickdf.empty:
                    print "keep current reuterfile and merge with the update of others from symbolfile"
                    symbolTable = self.mtd.loadSymbolLstFile(self.fileName)
                    df = symbolTable[symbolTable['rank']>0]
                    df = self.mtd.getSymbolByPid(df,self.pid)[['symbol','exg']]   
                    dfup = df[~df['symbol'].isin(reuterList)]
                    for co in self.columns:
                        dfup[co]=""
                    dfnc = reuterTable
                else:
                    print "keep current reuterfile and merge with the All updates from ticklist"
                    #dfup = self.tickdf[~self.tickdf['symbol'].isin(reuterList)]
                    ticklist = self.tickdf['symbol']
                    dfup = self.tickdf
                    for co in self.columns:
                        dfup[co]=""
                    dfnc = reuterTable[~reuterTable['symbol'].isin(ticklist)]                
                self.updateTickLst(dfnc,dfup)
            else:
                print "update current reuterfile only"
                dfnc = pandas.DataFrame({},columns=self.allcols)
                self.updateTickLst(dfnc,reuterTable)  
        else:
            if self.tickdf.empty:
                print "update symbolfile"
                symbolTable = self.mtd.loadSymbolLstFile(self.fileName)
                df = symbolTable[symbolTable['rank']>0]
                df = self.mtd.getSymbolByPid(df,self.pid)[['symbol','exg']]   
                dfup = df[['symbol','exg']]
                for co in self.columns:
                    dfup[co]=""
                dfnc = pandas.DataFrame({},columns=self.allcols)
                self.updateTickLst(dfnc,dfup)
            else:
                print "update ticklist only"
                dfnc = pandas.DataFrame({},columns=self.allcols)
                self.updateTickLst(dfnc,self.tickdf) 
            

    #usage
    def usage(self):
        print "reuterfunda.py -f symbollist.txt -t starttick -u update_tick_list -r reuter_result_csvfile"
       
        
    def process(self):
        self.parseOption()
        self.updateData()        
        #self.loadReuterCsvFile(self.fileName)
            
        print "Done,exit..."
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ReuterFunda()
    obj.process()
'''
  # update tick data    
    def updateData0(self): 
        #lenticklst = len(self.tickdf.index)       
        if self.reuterfile!="":
            self.updateTickLst(self.reuterfile,self.tickdf)
        else:
            symbolTable = self.mtd.loadSymbolLstFile(self.fileName)
            self.tickdf = symbolTable[symbolTable['rank']>0]
            self.updateTickLst("",self.tickdf)
             def updateData0(self): 
        lenticklst = len(self.ticklist)       
        symbolTable = self.mtd.loadSymbolLstFile(self.fileName)
        reuterTable = pandas.DataFrame()
        if self.reuterfile!="" and lenticklst>0:
            reuterTable = self.loadReuterCsvFile(self.reuterfile)
        outputfn = self.outputpath + "msdata_reuter_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'        
        outputfp = open(outputfn,'w',-1)        
         
        header = 'symbol,exg,' + ', '.join(self.columns) + "\n"
        outputfp.write(header)
          
        startFlag = True
        if self.starttick!="":
            startFlag = False
            print "wait for ",self.starttick
        
        print lenticklst
        for index, row in symbolTable.iterrows():
            if startFlag==False and row['symbol']!=self.starttick:
                continue
            else:
                startFlag=True

            rowLst = []
            #if row['symbol'] in self.ticklist:
            #    print row['symbol']
            if row['rank'] > 0 and ((lenticklst>0 and row['symbol'] in self.ticklist) or (lenticklst==0)):                
                print "downloading ",row['symbol'],row['exg']
                rowdct = self.getEarningData(row['symbol']+"."+row['exg'])                
                if len(rowdct)>0:
                    self.verifyCol(rowdct)
                    for key in self.columns:
                        if key in rowdct:
                            rowLst.append(rowdct[key])
                        else:
                            rowLst.append("")                
                    line = row['symbol'] + ',' + row['exg'] + ','  + ', '.join(rowLst) + "\n"
                    outputfp.write(line)
                    if index%10 == 0:
                        outputfp.flush()
                else:
                    print "No financials information,skip ",row['symbol'],row['exg']
                    #sys.exit()
            

        #merge with old reuter csv file
        #print reuterTable
        if not reuterTable.empty:
            for index, rowdct in reuterTable.iterrows():
                rowLst = []
                if rowdct['symbol'] in self.ticklist:
                    print "skip merge ",rowdct['symbol']
                    continue
                for key in self.columns:
                    if key in rowdct:
                        rowLst.append(str(rowdct[key]))
                    else:
                        rowLst.append("") 
                #print rowLst               
                line = rowdct['symbol'] + ',' + rowdct['exg'] + ','  + ', '.join(rowLst) + "\n"
                outputfp.write(line)
                
        outputfp.close()
        
         # update tick data    
    def updateData1(self): 
        lenticklst = len(self.tickdf.index)       
        #reuterTable = pandas.DataFrame()
        if self.reuterfile!="" and lenticklst>0:
            reuterTable = self.loadReuterCsvFile(self.reuterfile)
        else:
            return
        #outputfn = self.outputpath + "reuterfunda_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'        
        #outputfp = open(outputfn,'w',-1)        
        updatelst = self.tickdf['symbol']
        lf =  reuterTable[~reuterTable['symbol'].isin(updatelst)]
        
        #to update table
        allLst = {}
        allCol = ['symbol','exg'] + self.columns
        for key in allCol:
            lst = []
            allLst[key] = lst
        print "len of allLst",len(allLst) 
                
        print "total",lenticklst,"ticks to be updated"
        for index, row in self.tickdf.iterrows():
            rowLst = []
            print "downloading ",index,row['symbol'],row['exg']
            rowdct = self.getEarningData(row['symbol']+"."+row['exg'])                
            if len(rowdct)>0:
                self.verifyCol(rowdct)  
                for key in self.columns:
                    lst = allLst[key]
                    if key in rowdct:
                        lst.append(rowdct[key])
                    else:
                        lst.append("")   
                                     
                allLst['symbol'].append(row['symbol'])
                allLst['exg'].append(row['exg'])               
            else:
                print "No financials information,skip ",row['symbol'],row['exg']
                
        rf = pandas.DataFrame(allLst,columns = allCol)
        mf = lf.append(rf)
        mf.to_csv(self.outputfn,sep=',',index=False)
'''