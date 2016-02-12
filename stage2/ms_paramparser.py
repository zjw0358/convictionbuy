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
        self.verbose = False #print ohlc?
        pass
    #params = array(split)
    def parseOption(self, params):
        print "paramater:",params
        self.initParams()
                
        try:
            opts, args = getopt.getopt(params, "f:t:s:e:i:g:c:h", \
                ["filename", "ticklist", "startdate","enddate","pid","strategy","help","chart","savemd","loadmd","backtest","feed=","vb"])
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
        print "list",opts
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
            elif opt in ("--vb"):
                self.verbose = True
                
        if self.enddate == "":
            self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
        if not self.startdate:
            startday = datetime.date.today() - datetime.timedelta(days=365)
            self.startdate = startday.strftime("%Y-%m-%d")

        #if not self.sgyparam:
        #    self.sgyparam = self.loadCfg(self.mscfg)
            
        #load strategy
        #self.loadStrategy(self.sgyparam)           
        if self.help == True:
            sys.exit()

        print "use ", self.symbolLstFile
        print "start date", self.startdate
        print "end date", self.enddate
        print "portfolio id mask ",self.pid
        print "use chart",self.haschart
        if (self.haschart):
            print "chart param",self.chartparam
        print "load marketdata", self.loadmd
        print "save marketdata", self.savemd
        print "backtest", self.hasBackTest
        print "feeder", self.feed
        print "=========================="
        
        #if ("sina" in self.feed):
        #    self.sinaapi = SinaMarketData()
    def parseStrategy(self,arg):
        print "parseStrategy",arg
        l_sgy = {}
        for item in arg.split(","):
            idx = 0
            param = {}
            for token in item.split("&"):
                if idx == 0:                    
                    l_sgy[token] = param #first one is strategy
                else:
                    print "debug_test",token
                    if (token[0]!='@'): #we don't split by = if we see @,because @ is a metadata
                        k= token.split('=')
                        if (len(k)>1):
                            param[k[0]] = k[1]
                        else:
                            param[k[0]] = ""
                    else:
                        token = token[1:]
                        param[token] = ""
                idx += 1
        print l_sgy
        return l_sgy

    def getSymbolDf(self):
        if self.tickdf.empty:
            print "loading from symbolfile..."
            df = self.mtd.loadSymbolLstFile(self.symbolLstFile)
            df = self.mtd.getSymbolByPid(df,self.pid)[['symbol','sina','goog','googexg']]
        else:
            print "using ticklist from command line..."            
            df = self.tickdf  
        return df