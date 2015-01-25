# -*- coding: utf-8 -*-
import urllib2
import re
from bs4 import BeautifulSoup
import pandas
import marketdata
import datetime
import getopt
import sys

class ReuterFunda:
    '''
    get past 8 Quarter earning data from reuter
    '''
    def __init__(self):
        pandas.set_option('display.max_columns', 100)
        pandas.set_option('display.precision', 3)
        pandas.set_option('display.expand_frame_repr', False)
        #pandas.set_option('display.height', 1500)
        pandas.set_option('display.max_rows', 1500)
        self.mtd = marketdata.MarketData()
        self.outputpath = "../data/"
        self.fileName = ""
        self.starttick = ""
        #self.ticklist = ""

        
        
        
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

        #earning pasr quarter
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
                   
        #for seg in retmx:
        #    if retmx[seg]==0:
        #        return None
                         
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
        
    def updateData(self):        
        symbolTable = self.mtd.loadSymbolLstFile(self.fileName)
        outputfn = self.outputpath + "reuterfunda_" + datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'        
        outputfp = open(outputfn,'w',-1)
        
        columns = ['saleqtr0','saleqtr-1','saleqtr-2','saleqtr-3','saleqtr-4','saleqtr-5','saleqtr-6','saleqtr-7',\
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
             
        header = 'symbol,exg,' + ', '.join(columns) + "\n"
        outputfp.write(header)
        # prepare the table
        allData = {}
        for key in columns:
            lst = []
            allData[key] = lst
                
        startFlag = True
        if self.starttick!="":
            startFlag = False
            print "wait for ",self.starttick
        
        for index, row in symbolTable.iterrows():
            if startFlag==False and row['symbol']!=self.starttick:
                continue
            else:
                startFlag=True
            rowLst = []
            if row['rank'] > 0:
                #print index,row['symbol'],row['rank'],row['name']
                print "downloading ",row['symbol'],row['exg']
                rowdct = self.getEarningData(row['symbol']+"."+row['exg'])            
                
                if len(rowdct)>0:
                    self.verifyCol(rowdct)
                    for key in columns:
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
            
        outputfp.close()
        '''
        
            
        dct = self.getEarningData('msft.o')
        allLst = {}
        for key in columns:
            lst = []
            allLst[key] = lst
            if key in dct:
                lst.append(dct[key])
            else:
                lst.append('')
        table = pandas.DataFrame(allLst,columns=columns)
        ercol = ['saleqtr0','saleqtr-1','saleqtr-2','saleqtr-3','saleqtr-4','saleqtr-5','saleqtr-6','saleqtr-7',\
            'saleqtr-8','saleqtr-9','epsqtr0','epsqtr-1','epsqtr-2','epsqtr-3','epsqtr-4','epsqtr-5','epsqtr-6',\
            'epsqtr-7','epsqtr-8','epsqtr-9']
        print table[ercol]
        #print table
        return
        '''

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
            #return None
      
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
            #return None
       
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
            #return None
            
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
            #return None

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
            #return None
                      
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
            #return None

        tag = table.find("td",text=re.compile('[\d\D]*Price to Free Cash Flow \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppfcfttm'] = self.tofloat(cptag.string)
            valratio['indupfcfttm'] = self.tofloat(indutag.string)
            valratio['sectorpfcfttm'] = self.tofloat(sectortag.string)
        else:
            print "Price to Free Cash Flow (TTM) not found"
            #return None
        
        
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
            print "Dividend Yield - 5 Year Avg. not found"
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
        
    def tofloat(self,txt):
        if txt=="--" or txt==None:
            return ""
        else:
            return txt.replace(",","")
            
    def usage(self):
        print "program -f symbollist.txt -t ticklist"

              
    def parseOption(self):
        self.ticklist=[]
        try:
            opts, args = getopt.getopt(sys.argv[1:], "f:t:", ["filename", "start"])
        except getopt.GetoptError:
            return False
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.fileName = arg
            elif opt in ("-t", "--start"):
                self.starttick = arg

        if (self.fileName == ""):
            self.usage()
            sys.exit()
            
        print self.fileName,self.ticklist
        return
        
    def process(self):
        self.parseOption()
        self.updateData()
        print "Done,exit..."
################################################################################        
# main routine
################################################################################            
if __name__ == "__main__":
    obj = ReuterFunda()
    #zr.getEstimate('intc')
    #zr.getBrokerRecom('intc')
    #zr.getPriceSale('intc')
    obj.process()