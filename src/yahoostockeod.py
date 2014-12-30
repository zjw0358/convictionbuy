#!/usr/bin/python
import sys
import httplib
import urllib
import threading


import time
import datetime
import traceback
import metadata

ret = True

'''mysql> desc stockeod;
+-----------+-------------+------+-----+------------+-------+
| Field     | Type        | Null | Key | Default    | Extra |
+-----------+-------------+------+-----+------------+-------+
| symbol    | varchar(16) | NO   | PRI |            |       |
| sdate     | date        | NO   | PRI | 0000-00-00 |       |
| sopen     | double      | YES  |     | NULL       |       |
| shigh     | double      | YES  |     | NULL       |       |
| slow      | double      | YES  |     | NULL       |       |
| sclose    | double      | YES  |     | NULL       |       |
| sadjclose | double      | YES  |     | NULL       |       |
| volume    | bigint(20)  | YES  |     | NULL       |       |
+-----------+-------------+------+-----+------------+-------+
8 rows in set (0.02 sec)
'''

class httpget(threading.Thread):    
    def __init__ (self, symdict, dbconn):
        threading.Thread.__init__(self)        
        #self.url = "http://ichart.yahoo.com/table.csv?" + "s=" + symbol + "&c=" + starty + "&a=" + (startm-1) + "&b=" + startd + "&f=" + endy + "&d=" + (endm - 1) + "&e=" + endd +"&g=dignore=.csv";
        #today = datetime.date.today()
        #print today.year, today.month,today.day
        #self.url = "/table.csv?" + "s=" + symbol + "&c=" + str(lastdate.year) + "&a=" + str(lastdate.month-1) + "&b=" + str(lastdate.day)  + "&g=dignore=.csv"
        #url = "ichart.yahoo.com
        #self.host = "ichart.yahoo.com/table.csv?s=aapl&g=dignore=.csv"
        self.host = "ichart.yahoo.com"
        self.symdict = symdict
        self.dbconn = dbconn
        #print "url=%s" % self.url
        
    def run(self):
        cursor = self.dbconn.cursor()
        for key in self.symdict:
            self.download(key,self.symdict[key])
        
        

    def download(self,sym,lastdate):
        #lastdate = self.getStockEodLastDate(sym)
        #print lastdate
        #metadata.getStockEodLastDate(sym, self.dbconn)
        global ret

        #lastdate = pair[1]
        #sym = pair[0]
        print "downloading ",sym,lastdate
        

        tb=""
        cursor = self.dbconn.cursor()
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
                        #yahoo Date(0),Open(1),High(2),Low(3),Close(4),Volume(5),Adj Close(6)
                        
                        sql = "insert into stockeod(symbol,sdate,sopen,shigh,slow,sclose,volume,sadjclose) values ('%s', '%s', '%s', '%s', '%s','%s','%s','%s')" \
                          % (sym,eod[0],eod[1],eod[2], eod[3],eod[4],eod[5],eod[6])
                        #print sql
                        cursor.execute(sql)
                self.dbconn.commit()
                metadata.updateStockEodLastDate(sym, self.dbconn)
            except:
                print "yahoo download error"
                tb = traceback.format_exc()
                self.dbconn.rollback()
                print tb
                ret = False
            
        conn.close()
        return ret
    
        
def downloadStockEod(symdict,dbconn):
    threads = []
    for num in range(0, 1):
        thread = httpget(symdict,dbconn)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    
    return ret



