import metadata
import stockeod

import traceback
import datetime

default_cmd = "display"
'''def getLastDate(sym,dbconn):
    sql = "select lastdate from perfdata where symbol='%s'" % (sym);
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
        print "error"
        tb = traceback.format_exc()
        return 
    finally:        
        print tb

def updateLastDate(sym, dbconn):
    lastdate = datetime.date.today()
    sql = "update perfdata set lastdate='%s' where symbol='%s'" % (lastdate, sym);
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
'''



def resetTable(dbconn):
    sql = "delete from perfdata";
    cursor = dbconn.cursor()    
    try:
        tb=""
        cursor.execute(sql)
        dbconn.commit()
        return True
    except:
        print "error"
        tb = traceback.format_exc()
        dbconn.rollback()
        return False
    finally:
        print tb

def display(dbconn):
    print "%s performance 5 Y (%f / %f )= %f" % (sym,p_today,p_5y,p_today / p_5y)
    print "%s performance 2 Y = %.2f %%" % (sym,(p_today-p_2y)*100 / p_2y)
    print "%s performance 1 Y = %.2f %%" % (sym,(p_today-p_1y)*100 / p_1y)
    print "%s performance YTD = %.2f %%" % (sym,(p_today-p_ytd)*100 / p_ytd)
    print "%s performance 200 Day = %.2f %%" % (sym,p_today / p_200d)
    print "%s performance 100 Day = %f" % (sym,p_today / p_100d)
    print "%s performance 50 Day = %f" % (sym,p_today / p_50d)
    print "%s performance 20 Day = %f" % (sym,p_today / p_20d)
    print "%s performance 10 Day = %f" % (sym,p_today / p_10d)
    print "%s performance 5 Day = %f" % (sym,p_today / p_5d)


def addStockList(sym,lastDate,pf_y5d,pf_y2d,pf_y1d,pf_ytd,dbconn):
    cursor = dbconn.cursor()    
    try:
        tb=""        
        for sym in symlst:
            sql = "insert into perfdata(symbol) values ('%s')" % (sym)
            cursor.execute(sql)
        dbconn.commit()        

    except:
        print "error"
        tb = traceback.format_exc()
        dbconn.rollback()
    finally:
        print tb


def calc(dbconn):
    resetTable(dbconn)
    today = datetime.date.today()
    day_ytd = today.replace(month=1,day=1)
    day_5d = today-datetime.timedelta(days=5)
    day_10d = today-datetime.timedelta(days=10)
    day_20d = today-datetime.timedelta(days=20)
    day_50d = today-datetime.timedelta(days=50)
    day_100d = today-datetime.timedelta(days=100)
    day_200d = today-datetime.timedelta(days=200)
    day_1y = today.replace(year=today.year-1)
    day_2y = today.replace(year=today.year-2)
    day_5y = today.replace(year=today.year-5)
    symLst = metadata.getStockList(dbconn)
    for sym in symLst:
        # calculate
        p_today = stockeod.getLatestPrice(sym,dbconn)
        p_ytd = stockeod.getClosePrice(sym,day_ytd,dbconn)
        p_1y = stockeod.getClosePrice(sym,day_1y,dbconn)
        p_2y = stockeod.getClosePrice(sym,day_2y,dbconn)
        p_5y = stockeod.getClosePrice(sym,day_5y,dbconn)
        p_5d = stockeod.getClosePrice(sym,day_5d,dbconn)
        p_10d = stockeod.getClosePrice(sym,day_10d,dbconn)
        p_20d = stockeod.getClosePrice(sym,day_20d,dbconn)
        p_50d = stockeod.getClosePrice(sym,day_50d,dbconn)
        p_100d = stockeod.getClosePrice(sym,day_100d,dbconn)
        p_200d = stockeod.getClosePrice(sym,day_200d,dbconn)
        pf_5y = (p_today-p_5y)*100/p_5y
        pf_2y = (p_today-p_2y)*100/p_2y
        pf_1y = (p_today-p_1y)*100/p_1y
        pf_ytd = (p_today-p_ytd)*100/p_ytd
        pf_200d = (p_today-p_200d)*100/p_200d
        pf_100d = (p_today-p_100d)*100/p_100d
        pf_50d = (p_today-p_50d)*100/p_50d
        pf_20d = (p_today-p_20d)*100/p_20d
        pf_10d = (p_today-p_10d)*100/p_10d
        pf_5d = (p_today-p_5d)*100/p_5d
        cursor = dbconn.cursor()    
        try:
            tb=""        
            sql = "insert into perfdata(symbol,lastdate,y5d,y2d,y1d,ytd,td200,td100,td50,td20,td10,td5) \
                    values ('%s','%s',%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f)" \
                    % (sym,today,pf_5y,pf_2y,pf_1y,pf_ytd,pf_200d,pf_100d,pf_50d,pf_20d,pf_10d,pf_5d)
            cursor.execute(sql)
            dbconn.commit()
        except:
            print "error"
            tb = traceback.format_exc()
            dbconn.rollback()
        finally:
            #print tb
            return

# get the date performance
def queryOneDatePerf(sym,thedate,dbconn):
    dayago = thedate-datetime.timedelta(days=1)
    p0=stockeod.getClosePriceS(sym,dayago,dbconn)
    p1=stockeod.getClosePriceS(sym,thedate,dbconn)
    chg=(p1-p0)*100/p0
    return chg

# make it more common?
def queryYtdPerf(sym,dbconn):
    today = datetime.date.today()
    day_ytd = today.replace(month=1,day=1)
    #day_ytd = jan1-datetime.timedelta(days=1)
    #print sym,day_ytd,today
    p0=stockeod.getClosePriceS(sym,day_ytd,dbconn)
    if p0==None:#BABA ipo at 2014-9-19
        p0=stockeod.getClosePriceB(sym,day_ytd,dbconn)
    p1=stockeod.getClosePriceS(sym,today,dbconn)
    chg=(p1-p0)*100/p0
    return chg
    
def process(actions,dbconn):
    cmd = ""
    
    if len(actions)<2:
        return
    #elif len(actions)>2:
    #    args = actions[2]
    cmd = actions[1]
    if cmd=="display":
        calc(dbconn)
    elif cmd=="query":
        args = actions[2:]
        if len(args)<2:
            return
        #args.split(',')
        thedate = datetime.datetime.strptime(args[1],'%Y-%m-%d')
        ret = "%s=%.2f %%" % (args[0],queryPerf(args[0],thedate,dbconn))
        print ret
        #print args[0], "=", queryPerf(args[0],thedate,dbconn) , "%"
        
