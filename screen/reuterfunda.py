import urllib2
import re
from bs4 import BeautifulSoup

class ReuterFunda:
    '''
    get past 8 Quarter earning data from reuter
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
            return False
            
        soup = BeautifulSoup(page)

        #earning pasr quarter
        dataTableLst = soup.findAll("table",attrs={'class':"dataTable"})
        retmx={'er':0,'vr':0,'gr':0,'me':0,'mrg':0}
    
        retdct = {}
        for table in dataTableLst:
            if retmx['er'] == 0:
                ret=self.parsePastQEarning(table)
                if ret!=None:
                    retmx['er'] = 1
                    retdct['er']=ret
                    continue
                    
            if retmx['vr'] == 0:
                ret=self.parseValuationRatio(table)
                if ret!=None:
                    retmx['vr'] = 1
                    retdct['vr'] = ret
                    continue
                                        
            if retmx['gr'] == 0:
                ret = self.parseGrowth(table)
                if ret!=None:
                    retmx['gr'] = 1
                    retdct['gr'] = ret
                    continue
                    
            if retmx['mrg'] == 0:
                ret=self.parseProfitRatio(table)
                if ret!=None:
                    retmx['mrg'] = 1
                    retdct['mrg'] = ret
                    continue
                                        
            if retmx['me'] == 0:
                ret = self.parseMangEffect(table)
                if ret!=None:
                    retmx['me'] = 1
                    retdct['me']=ret
                    continue
                   
                    
        print retdct             
        return 
        


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
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Investment \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproi'] = self.tofloat(cptag.string)
            mangeff['induroi'] = self.tofloat(indutag.string)
            mangeff['sectorroi'] = self.tofloat(sectortag.string)
        else:
            return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Return on Investment - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproi5y'] = self.tofloat(cptag.string)
            mangeff['induroi5y'] = self.tofloat(indutag.string)
            mangeff['sectorroi5y'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Equity \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproe'] = self.tofloat(cptag.string)
            mangeff['induroe'] = self.tofloat(indutag.string)
            mangeff['sectorroe'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Return on Equity - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            mangeff['cproe5y'] = self.tofloat(cptag.string)
            mangeff['induroe5y'] = self.tofloat(indutag.string)
            mangeff['sectorroe5y'] = self.tofloat(sectortag.string)
        else:
            return None
        
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
                   salekey = "R%d" % (idx/2)
                   epskey = "Q%d" % (idx/2)
                   if idx%2 == 0:
                       reveps[salekey] = self.tofloat(data.string)
                   else:
                       reveps[epskey] = self.tofloat(data.string)
                   idx += 1                
                return reveps
            return None
        else:
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
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Operating Margin \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpom'] = self.tofloat(cptag.string)
            profitratio['induom'] = self.tofloat(indutag.string)
            profitratio['sectorom'] = self.tofloat(sectortag.string)
        else:
            return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Operating Margin - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpom5y'] = self.tofloat(cptag.string)
            profitratio['induom5y'] = self.tofloat(indutag.string)
            profitratio['sectorom5y'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Net Profit Margin \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpnm'] = self.tofloat(cptag.string)
            profitratio['indunm'] = self.tofloat(indutag.string)
            profitratio['sectornm'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Net Profit Margin - 5 Yr\. Avg\.[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            profitratio['cpnm5y'] = self.tofloat(cptag.string)
            profitratio['indunm5y'] = self.tofloat(indutag.string)
            profitratio['sectornm5y'] = self.tofloat(sectortag.string)
        else:
            return None
        
        return profitratio

    def parseValuationRatio(self,table):
        valratio = {}

        tag = table.find("td",text=re.compile('[\d\D]*Price to Cash Flow \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppcf'] = self.tofloat(cptag.string)
            valratio['indupcf'] = self.tofloat(indutag.string)
            valratio['sectorpcf'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Price to Free Cash Flow \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppfcf'] = self.tofloat(cptag.string)
            valratio['indupfcf'] = self.tofloat(indutag.string)
            valratio['sectorpfcf'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Beta[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cpbeta'] = self.tofloat(cptag.string)
            valratio['indubeta'] = self.tofloat(indutag.string)
            valratio['sectorbeta'] = self.tofloat(sectortag.string)
        else:
            return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Price to Sales \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cpps'] = self.tofloat(cptag.string)
            valratio['indups'] = self.tofloat(indutag.string)
            valratio['sectorps'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Price to Book (MRQ)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppb'] = self.tofloat(cptag.string)
            valratio['indupb'] = self.tofloat(indutag.string)
            valratio['sectorpb'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*P/E Ratio \(TTM\)[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            valratio['cppe'] = self.tofloat(cptag.string)
            valratio['indupe'] = self.tofloat(indutag.string)
            valratio['sectorpe'] = self.tofloat(sectortag.string)
        else:
            return None
        
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
            return None

        tag = table.find("td",text=re.compile('[\d\D]*Sales - 5 Yr\. Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpsale5ygr'] = self.tofloat(cptag.string)
            gr['indusale5ygr'] = self.tofloat(indutag.string)
            gr['sectorsale5ygr'] = self.tofloat(sectortag.string)
        else:
            return None
            
        tag = table.find("td",text=re.compile('[\d\D]*EPS \(MRQ\) vs Qtr\. 1 Yr\. Ago[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpepsmrqyoy'] = self.tofloat(cptag.string)
            gr['induepsmrqyoy'] = self.tofloat(indutag.string)
            gr['sectorepsmrqyoy'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*EPS \(TTM\) vs TTM 1 Yr\. Ago[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpepsttmyoy'] = self.tofloat(cptag.string)
            gr['induepsttmyoy'] = self.tofloat(indutag.string)
            gr['sectorepsttmyoy'] = self.tofloat(sectortag.string)
        else:
            return None

        tag = table.find("td",text=re.compile('[\d\D]*EPS - 5 Yr\. Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpeps5ygr'] = self.tofloat(cptag.string)
            gr['indueps5ygr'] = self.tofloat(indutag.string)
            gr['sectoreps5ygr'] = self.tofloat(sectortag.string)
        else:
            return None
            
        tag = table.find("td",text=re.compile('[\d\D]*Capital Spending - 5 Yr\. Growth Rate[\d\D]*'))        
        if tag!=None:
            cptag = tag.nextSibling.nextSibling
            indutag = cptag.nextSibling.nextSibling            
            sectortag = indutag.nextSibling.nextSibling
            gr['cpcap5ygr'] = self.tofloat(cptag.string)
            gr['inducap5ygr'] = self.tofloat(indutag.string)
            gr['sectorcap5ygr'] = self.tofloat(sectortag.string)
        else:
            return None
        return gr
        
    def tofloat(self,txt):
        return txt.replace(",","")
        
    def process(self):
        self.getEarningData('msft.o')
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