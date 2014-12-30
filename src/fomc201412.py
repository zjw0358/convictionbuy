import traceback
import datetime
import perfdata
import metadata
import stocklist

import pandas


def beatspx(thedate,dbconn):
    symlst = metadata.getStockList("default",dbconn)
    beatspxlst = pandas.DataFrame(columns=('symbol', 'sector', 'chg'))
    beapspxchg = 0.0
    for symbol in symlst:
        chg = perfdata.queryOneDatePerf(symbol,thedate,dbconn)        
        if chg>2.04:
            sector = stocklist.getSector(symbol,dbconn)
            #beatspxlst[symbol] = sector
            beatspxlst.loc[len(beatspxlst)+1]=[symbol,sector,chg] 
            print "choose ",symbol,",",sector,"=",chg   
    # de-duplicated by sector
    #lst1 = pandas.Series(beatspxlst)
    beatspxlst = beatspxlst.sort_index(by="chg",ascending=False)
    print beatspxlst
    print "========================="
    beatspxlst = beatspxlst.drop_duplicates(cols='sector')
    print beatspxlst['symbol']
    
    for symbol in beatspxlst['symbol']:
        chg = perfdata.queryYtdPerf(symbol,dbconn)
        
        beapspxchg += chg 
        print symbol,",",sector,"=",chg     
    print "beapspx YTD performance=", beapspxchg
    

def calc(thedate,dbconn):
    symlst = metadata.getStockList("default",dbconn)
    #symdict = {}
    totalchg = 0.0;
    top10 = 0.0
    for symbol in symlst:
        #print symbol
        chg = perfdata.queryYtdPerf(symbol,dbconn)
        print chg
        totalchg += chg
        if chg>2.04:
            top10+=chg
        #chg = perfdata.queryPerf(symbol,thedate,dbconn)
        #ret = "%s=%.2f %%" % (symbol,chg)
        #symdict[symbol] = chg
        #print ret
    print "YTD performance=", totalchg
    print "TOP spx YTD performance=", top10
    #symdict= sorted(symdict.iteritems(), key=lambda d:d[1], reverse = True)
    #print symdict
    
def help():
    print "program fomc date"
    
def process(actions,dbconn):
    #print actions
    if len(actions)==0:
        return
    if actions[0]=="help":
        help()
        return
    thedate = datetime.datetime.strptime(actions[0],'%Y-%m-%d')
    beatspx(thedate,dbconn)
