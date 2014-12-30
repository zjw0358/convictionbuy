import datetime
import traceback
from pandas import DataFrame
import pandas.io.sql as sql

def getClosePriceB(sym,thedate,dbconn):
    sql = "select sadjclose from stockeod where symbol='%s' and sdate>='%s' order by sdate asc limit 5" % (sym,thedate);
    cursor = dbconn.cursor()
    try:
        tb=""
        cursor.execute(sql)
        results = cursor.fetchall()
        for d in results:
            #print sym, "=", d[0], "=", results
            return d[0]

    except:
        print "error"
        tb = traceback.format_exc()
        print tb
        return
def getClosePriceS(sym,thedate,dbconn):
    sql = "select sadjclose from stockeod where symbol='%s' and sdate<='%s' order by sdate desc limit 5" % (sym,thedate);
    cursor = dbconn.cursor()
    try:
        tb=""
        cursor.execute(sql)
        results = cursor.fetchall()
        for d in results:
            #print sym, "=", d[0], "=", results
            return d[0]

    except:
        print "error"
        tb = traceback.format_exc()
        print tb
        return

def getAllDataFrame(sym,startdate,dbconn):
    print "getAllDataFrame",sym,startdate
    sqlstr = "select * from stockeod where symbol='%s' and sdate>='%s'" % (sym,startdate);
    #cursor = dbconn.cursor()
    try:
        tb=""
        #cursor.execute(sql)
        df = sql.read_frame(sqlstr, dbconn)
        #results = cursor.fetchall()
        #df = DataFrame(cursor.fetchall())
        #df.columns = cursor.keys()    
        return df
        
        #import MySQLdb as mdb

        #from pandas import *

        #conn = mdb.connect('<server>','<user>','<pass>','<db>');
        




    except:
        print "error"
        tb = traceback.format_exc()
        print tb
        return
                     
def getLatestPrice(sym,dbconn):
    today = datetime.date.today()
    sql = "select sadjclose from stockeod where symbol='%s' and sdate<='%s' order by sdate desc limit 5" % (sym,today);
    cursor = dbconn.cursor()
    try:
        tb=""
        cursor.execute(sql)
        results = cursor.fetchall()
        for d in results:
            #print sym, "=", d, "=", results
            return d[0]

    except:
        print "error"
        tb = traceback.format_exc()
        return
    finally:        
        print tb
