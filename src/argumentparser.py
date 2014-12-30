import getopt
import sys

db_username = "root"
db_passwd = "cv80faqq"
dbname = "candy"
action = []
sym_lst = []


# parse command line args
# symbol list would be : 
'''
NYSE:DOW  NYSE:PEP  NYSE:CVX  NYSE:WMT  NYSE:MMM  NYSE:CAT  NYSE:XOM  NYSE:COP  NYSE:KO  NYSE:CL  NYSE:KMB  NYSE:MCD  NYSE:GE  NYSE:BA  NYSE:NOC  NYSE:MRK  NYSE:GSK  NYSE:NVS  NYSE:PG  NYSE:JNJ  NYSE:MJN  NYSE:ABT  NYSE:LLY  NYSE:PFE  NYSE:BMY  NYSE:SNY  NASDAQ:BIIB  NYSE:AZN  NASDAQ:GILD  NYSE:BLK  NYSE:AXP  NYSE:MA  NYSE:V  NYSE:C  NYSE:BAC  NYSE:JPM  NYSE:WFC  NYSE:GM  NYSE:F  NYSE:MS  NASDAQ:ERIC  NYSE:NOK  NASDAQ:NTES  NASDAQ:BBRY  NYSE:QIHU  NASDAQ:SOHU  NASDAQ:CYOU  NYSE:VIPS  NYSE:LITB  NYSE:BABA  NASDAQ:WB  NASDAQ:YY  NYSE:VMW  NASDAQ:NFLX  NASDAQ:AMZN  NASDAQ:GOOGL  NASDAQ:GOOG  NYSE:LMT  NYSE:A  NYSE:GS  NASDAQ:BIDU  NYSE:ORCL  NASDAQ:FB  NYSE:TWTR  NYSE:EMC  NASDAQ:AAPL  NASDAQ:JDSU  NASDAQ:CSCO  NYSE:T  NYSE:VZ  NASDAQ:MSFT  NYSE:SAP  NASDAQ:INTC  NYSE:IBM  NASDAQ:QCOM  NASDAQ:TSLA  NYSE:COH  NYSE:RTN  NYSE:CBI  NYSE:HD  NYSE:DIS  NASDAQ:FOXA
'''
def parse():
    global db_username
    global db_passwd
    global dbname
    global sym_lst
    global action
    global component
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:d:s:", ["username", "passwd","dbname","symbolist"])
    except getopt.GetoptError:
        return False
    for opt, arg in opts:
        if opt in ("-u", "--username"):
            db_username = arg
        elif opt in ("-p", "--passwd"):
            db_passwd = arg
        elif opt in ("-d", "--dbname"):
            dbname = arg
        elif opt in ("-s", "--symbolist"):
            symstr = arg
            sym_lst = symstr.split()
    
    print "argument:",args
    for index in range(len(args)):
        #if len(action)>index:
        #    action[index] = args[index]
        #else:
        action.append(args[index])
        print "action[",index,"]=",action[index]

    return True
    #if (self.intput_file==""):
    #    raise Exception("argument missing")
    #if (self.expect_file==""):
    #    raise Exception("argument missing")
