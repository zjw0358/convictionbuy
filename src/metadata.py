import traceback
import datetime
import yahoostockeod

default_portfolio = "default"

def getStockEodLastDate(sym,dbconn):
    sql = "select lastdate from stockmetadata where symbol='%s' and portfolio='%s'" % (sym,default_portfolio);
    cursor = dbconn.cursor()
    try:
        tb=""
        cursor.execute(sql)
        results = cursor.fetchone()
        for d in results:        
            if d==None:
                return datetime.datetime(1990,1,1)
            else:                
                return d

    except:
        print "getStockEodLastDate error"
        tb = traceback.format_exc()
        return 
    finally:        
        #print tb
        return

def getAllStockNLastDate(dbconn):
    sql = "select symbol,lastdate from stockmetadata where portfolio='%s'" % (default_portfolio);
    cursor = dbconn.cursor()
    symdict={}
    tb=""
    try:
        print sql
        cursor.execute(sql)
        results = cursor.fetchall()
        for pair in results:
            #print pair[0]
            if pair[1]==None:
                symdict[pair[0]]=datetime.datetime(1990,1,1)
                #print symdict
            else:
                symdict[pair[0]] = pair[1]
        #print symdict                      
        
    except:
        print "getAllStockNLastDate error"
        tb = traceback.format_exc()
        print tb
        return 
    finally: 
        return symdict

def updateStockEodLastDate(sym, dbconn):
    lastdate = datetime.date.today()
    sql = "update stockmetadata set lastdate='%s' where symbol='%s' and portfolio='%s'" % (lastdate, sym, default_portfolio);
    print sql
    cursor = dbconn.cursor()
    tb=""
    try:            
        cursor.execute(sql)
        dbconn.commit()

    except:
        print "error"
        tb = traceback.format_exc()
        dbconn.rollback()
    finally:        
        print tb

def addStockList(symlst,pf,dbconn):
    cursor = dbconn.cursor()    
    try:
        tb=""
        for sym in symlst:
            syminfo = sym.split(':') # NYSE:BABA -> NYSE, BABA
            exg = ""
            thesym = ""
            if len(syminfo)==2:
                thesym = syminfo[1]
                exg = syminfo[0]
            else:
                thesym = sym
            try:
                sql = "insert into stockmetadata(symbol,portfolio) values ('%s','%s')" % (thesym,pf)
                cursor.execute(sql)
            except:
                print "stockmetadata insert error=",sql
                
        dbconn.commit()        
        print "add stockmetadata done"
    except:
        print "add stock metadata error"
        tb = traceback.format_exc()
        print tb
        dbconn.rollback()
    finally:
        return
        #print tb


def getStockList(pf,dbconn):
    sql = "select symbol from stockmetadata where portfolio='%s'" % (pf);
    cursor = dbconn.cursor()
    symlst = []
    try:
        tb=""
        cursor.execute(sql)
        results = cursor.fetchall()            

        for row in results:
            symlst.append(row[0])
        
        return symlst

    except:
        print "getStockList error"
        tb = traceback.format_exc()
        print tb
    

def process(symlst,actions,dbconn):
    pf = ""
    if len(actions)==2:
        pf = default_portfolio 
        #print  "is",  default_portfolio    
    elif len(actions)>2:
        pf = actions[2]
    else:
        return
    if (actions[1]=="add"):
        #print symlst
        addStockList(symlst,pf,dbconn)
    elif actions[1]=="list":
        print "portfolio '",pf, "' list=", getStockList(pf,dbconn)
    elif actions[1]=="download":
        symdict = getAllStockNLastDate(dbconn)
        yahoostockeod.downloadStockEod(symdict,dbconn)
    elif actions[1]=="forcedownload":
        symdict = getAllStockNLastDate(dbconn)
        for key in symdict:
            symdict[key]=datetime.datetime(1990,1,1)
            #yahoostockeod.deletestock(symbol)
        yahoostockeod.downloadStockEod(symdict,dbconn)

