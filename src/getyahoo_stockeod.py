#!/usr/bin/python
import sys
import httplib
import urllib
import threading

import MySQLdbconn
import time
import datetime
import traceback




 


class httpget(threading.Thread):    
    def __init__ (self, symlst, dbconn):
        threading.Thread.__init__(self)        
        #self.url = "http://ichart.yahoo.com/table.csv?" + "s=" + symbol + "&c=" + starty + "&a=" + (startm-1) + "&b=" + startd + "&f=" + endy + "&d=" + (endm - 1) + "&e=" + endd +"&g=dignore=.csv";
        #today = datetime.date.today()
        #print today.year, today.month,today.day
        #self.url = "/table.csv?" + "s=" + symbol + "&c=" + str(lastdate.year) + "&a=" + str(lastdate.month-1) + "&b=" + str(lastdate.day)  + "&g=dignore=.csv"
        self.host = "ichart.yahoo.com"
        self.symlst = symlst
        self.dbconn = dbconn
        print "url=%s" % self.url
        
    def run(self):
        cursor = self.dbconn.cursor()
        for (symbol in self.symlst):
            download(symbol)
        
        

    def download(self,sym):
        lastdate = getStockEodLastDate(sym)
        tb=""
        url = "/table.csv?" + "s=" + sym + "&c=" + str(lastdate.year) + "&a=" + str(lastdate.month-1) + "&b=" + str(lastdate.day)  + "&g=dignore=.csv"
        conn = httplib.HTTPConnection(self.host)        
        conn.request('GET', url)
        response = conn.getresponse()
        if response.status != httplib.OK:
            print "FAIL Output from  request\n" 
            #printText (response.read())
        else:
            data=response.read()
            try:
                lines = data.split('\n')
                #skip first line
                for i in range(1,len(lines)):
                    line = lines[i]                    
                    if (line!=""):
                        eod = line.split(',')
                        #print eod[0],eod[1]
                        
                        sql = "insert into stockeod(symbol,sdate,sopen,sclose,shigh,slow,sadjclose,volumn) values ('%s', '%s', '%s', '%s', '%s','%s','%s','%s')" \
                          % (self.sym,eod[0],eod[1],eod[2],eod[3],eod[4],eod[6],eod[5])
                        print sql
                        cursor.execute(sql)
                        self.dbconn.commit()
            except:
                print "download error"
                tb = traceback.format_exc()
                self.dbconn.rollback()
            finally:
                print tb
        conn.close()

    def getStockEodLastDate(sym):
        sql = "select lastdate from keystats where symbol='%s'" % (sym);
        cursor = self.dbconn.cursor()
        try:
            tb=""
            cursor.execute(sql)
            results = cursor.fetchall()            

            for row in results:
                return (row[0])
            
            return datetime.datetime(2014,12,1)

        except:
            print "error"
            tb = traceback.format_exc()
            
        finally:        
            print tb


def downloadStockEod(symlst,dbconn):
    threads = []
    for num in range(0, 1):
        thread = httpget(symlst,dbconn)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    
#lastdate = datetime.datetime(2014,12,1)
#print "lastdate=%s" % (lastdate)
#params = urllib.urlencode({'req': content})
#headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}


