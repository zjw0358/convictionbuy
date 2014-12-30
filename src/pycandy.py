# -*- coding: utf-8 -*-
import MySQLdb
import sys

import yahoostockeod
import metadata
import argumentparser
import resetdb
import perfdata
import stocklist
import fomc201412
import vola
import stchart

def usage():
    print "python program -u usrname -p passwd -d dbname [-s symbollist]"

#if (len(sys.argv) < 4):
#  usage()
#   exit()

#username = sys.argv[1]
#passwd = sys.argv[2]
#dbname = sys.argv[3]
#symstr = sys.argv[4]
#symlst = symstr.split(',')

ret = argumentparser.parse()
#ret=True
#print ret
if (ret==True):
    dbconn = MySQLdb.connect("localhost",argumentparser.db_username,argumentparser.db_passwd,argumentparser.dbname)
    if argumentparser.action[0]=="portfolio":
        metadata.process(argumentparser.sym_lst,argumentparser.action,dbconn)
        #perfdata.addStockList(argumentparser.sym_lst,dbconn)
    #elif argumentparser.action[0]=="listportfolio":
    #    print metadata.getStockList(dbconn)
    #elif argumentparser.action[0]=="download":
    #    sym_lst = metadata.getStockList(dbconn)
    #    yahoostockeod.downloadStockEod(sym_lst,dbconn)
    elif argumentparser.action[0]=="resetdb":
        resetdb.reset(dbconn)
    elif argumentparser.action[0]=="perf":
        perfdata.process(argumentparser.action[1:],dbconn)
    elif argumentparser.action[0]=="stocklist":
        stocklist.process(argumentparser.action[1:],dbconn)
    elif argumentparser.action[0]=="fomc": # strategy study
        fomc201412.process(argumentparser.action[1:],dbconn)
    elif argumentparser.action[0]=="vola": # strategy study
        vola.process(argumentparser.action[1:],dbconn)
    elif argumentparser.action[0]=="chart": # strategy study
        stchart.process(argumentparser.action[1:],dbconn)
    dbconn.close()
