#!/usr/bin/python

import MySQLdb
import time
import datetime
import traceback
import sys


def process(username, passwd, dbname, sym, date):
    db = MySQLdb.connect("localhost",username,passwd,dbname )    
    d5 = getDoubleDaysAgoTime(5)
    d10 = getDoubleDaysAgoTime(10)
    d20 = getDoubleDaysAgoTime(20)
    d50 = getDoubleDaysAgoTime(50)
    d100 = getDoubleDaysAgoTime(100)
    strd100 = getStrDaysAgoTime(100)

    sql = "select shigh,slow,sdate from stockeod where symbol='%s' and sdate>='%s'" % (sym,strd100);
    cursor = db.cursor()
    try:
        tb=""
        cursor.execute(sql)
        results = cursor.fetchall()
        high5 = 0
        low5 = 1000000
        
        high10 = 0
        low10 = 1000000
        
        high20 = 0
        low20 = 1000000
        
        high50 = 0
        low50 = 1000000
        
        high100 = 0
        low100 = 1000000
        
        high52w = 0
        low52w = 1000000

        for row in results:
            if (row[2]>=d5):
                high5 = max(row[0], high5)
                low5  = min(row[1],low5)
                
            if (row[2]>=d10):
                high10 = max(row[0], high10)
                low10  = min(row[1],low10)

            if (row[2]>=d20):
                high20 = max(row[0], high20)
                low20  = min(row[1],low20)

            if (row[2]>=d50):
                high50 = max(row[0], high50)
                low50  = min(row[1],low50)

            if (row[2]>=d100):
                high100 = max(row[0], high100)
                low100  = min(row[1],low100)
            
            
            
          

        print "5 day high=%.2f,5 day low=%.2f" % (high5, low5)
        print "10 day high=%.2f,10 day low=%.2f" % (high10, low10)
        print "20 day high=%.2f,20 day low=%.2f" % (high20, low20)
        print "50 day high=%.2f,50 day low=%.2f" % (high50, low50)
        print "100 day high=%.2f,100 day low=%.2f" % (high100, low100)



        db.commit()
    except:

        print "error"
        tb = traceback.format_exc()
        db.rollback()
    finally:

        db.close()
        print tb

def getCurrentTime():
    return time.strftime('%Y-%m-%d',time.localtime(time.time()))

def getDoubleDaysAgoTime(ago):
    #today = time.time()
    #daysago = today - ago*60*60*24
    #return datetime.time(daysago)
    return (datetime.date.today()-datetime.timedelta(days=ago))
    

def getStrDaysAgoTime(ago):
    today = time.time()
    daoago = today - ago*60*60*24
    return time.strftime('%Y-%m-%d',time.localtime(daoago))

def usage():
    print "Usage: program username password db symbol"    

if __name__ == "__main__":
    if (len(sys.argv) < 5):
        usage()
        exit()
    username = sys.argv[1]
    passwd = sys.argv[2]
    dbname = sys.argv[3]
    symbol = sys.argv[4]
    today = getCurrentTime()
    
    getHisData(username,passwd,dbname,symbol, today)

    

