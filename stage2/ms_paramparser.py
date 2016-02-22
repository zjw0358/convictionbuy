'''
parameter parser
'''
import getopt
import sys
import pandas
import datetime
import marketdata
import ms_config

class ms_paramparser:
    def __init__(self):
        #TODO move parse pid here later
        self.mtd = marketdata.MarketData()
        self.cfg = ms_config.MsDataCfg("") 
        self.symbolLstFile = self.cfg.getDataConfig("marketdata") 
        self.initParams()
        pass
        
    def initParams(self):
        self.enddate = ""
        self.startdate = ""
        self.help = False
        self.haschart = False
        self.savemd = False
        self.loadmd = False
        self.hasBackTest = False
        self.feed = ""  # yahoo feeder
        self.pid = 1 #0-dow30,1-zr focus list,2-jpm/zack list
        self.tickdf = pandas.DataFrame({},columns=['symbol','exg','sina','goog','googexg'])                
        self.sgyparam = {}
        self.verbose = 0
        self.tailoffset = 0
        pass
    #params = array(split)
    def parseOption(self, params, display=True):
        #print "paramater:",params
        self.initParams()
                
        try:
            opts, args = getopt.getopt(params, "v:f:t:s:e:i:g:c:h",
                ["filename", "ticklist", "startdate", "enddate", "pid", "strategy", "help", "chart", "savemd",
                 "loadmd", "backtest", "feed=", "verbose", "tailoffset=", "buy=", "sell="])
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
            
        if (display):
            print "%-20s:%-50s" % ("parameter dict",opts)
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                self.symbolLstFile = arg
                #self.option = 1
            elif opt in ("-t", "--ticklist"):
                #tdict = self.mtd.parseTickLst(arg)
                #self.tickdf = pandas.DataFrame(list(tdict.iteritems()),columns=['symbol','exg'])                
                self.tickdf = self.mtd.parseTickLstDf(arg)
            elif opt in ("-s", "--startdate"):
                self.startdate = arg
            elif opt in ("-e", "--enddate"):
                self.enddate = arg
            elif opt in ("-i", "--pid"):
                idLst = arg.split(",")
                self.pid = self.mtd.parsePidLst(idLst)
            elif opt in ("-g", "--strategy"):
                self.sgyparam = self.parseStrategy(arg)
            elif opt in ("-h", "--help"):
                self.usage()
                self.help=True                                   
            elif opt in ("-c","--chart"):
                self.haschart = True
                self.chartparam = arg
            elif opt in ("--backtest"):
                self.hasBackTest = True
                #self.backtest = ms_backtest.ms_backtest()
            elif opt in ("--savemd"):
                self.savemd = True
            elif opt in ("--loadmd"):
                self.loadmd = True
            elif opt in ("--feed"):
                self.feed = arg
            elif opt in ("-v","--verbose"):
                self.verbose = int(arg)
            elif opt in ("--tailoffset"):
                self.tailoffset = int(arg)
            elif opt in ("--buy"):
                self.buydict = self.parseBuy(arg)
            elif opt in ("--sell"):
                self.selldict = self.parseSell(arg)

        if self.enddate == "":
            self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
        if not self.startdate:
            startday = datetime.date.today() - datetime.timedelta(days=365)
            self.startdate = startday.strftime("%Y-%m-%d")

        
        #if self.help == True:
        #    sys.exit()
        if (display):
            print "%-20s: %-50s" % ("use", self.symbolLstFile)
            print "%-20s: %-50s" % ("start date", self.startdate)
            print "%-20s: %-50s" % ("end date", self.enddate)
            print "%-20s: %-50s" % ("portfolio id mask ",self.pid)
            print "%-20s: %-50s" % ("use chart",self.haschart)
            if (self.haschart):
                print "%-20s: %-50s" % ("chart param",self.chartparam)
            print "%-20s: %-50s" % ("load marketdata", self.loadmd)
            print "%-20s: %-50s" % ("save marketdata", self.savemd)
            print "%-20s: %-50s" % ("backtest", self.hasBackTest)
            print "%-20s: %-50s" % ("feeder", self.feed)
            print "%-20s: %-50s" % ("verbose", self.verbose)
            print "...................."

        return opts

    def parseBuy(self, arg):
        tokens = arg.split(',')

        self.buydict = self.parseBuy(arg)


    def parseStrategy(self,arg):
        #print "parseStrategy",arg
        l_sgy = {}
        for item in arg.split(","):
            idx = 0
            param = {}
            for token in item.split("&"):
                if idx == 0:                    
                    l_sgy[token] = param #first one is strategy
                else:
                    #print "debug_test",token
                    if (token[0]!='@'): #we don't split by = if we see @,because @ is a metadata,e.g. @colname=4
                        k= token.split('=')
                        if (len(k)>1):
                            param[k[0]] = k[1]
                        else:
                            param[k[0]] = ""
                    else:
                        token = token[1:]
                        param[token] = ""
                idx += 1
        #print l_sgy
        return l_sgy

    def getSymbolDf(self):
        if self.tickdf.empty:
            if (self.verbose>0):
                print "loading from symbolfile..."
            df = self.mtd.loadSymbolLstFile(self.symbolLstFile)
            df = self.mtd.getSymbolByPid(df,self.pid)[['symbol','sina','goog','googexg']]
        else:
            if (self.verbose>0):
                print "using ticklist from command line..."            
            df = self.tickdf  
        return df