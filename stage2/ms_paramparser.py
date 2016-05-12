import getopt
import sys
import pandas
import datetime
import marketdata
import ms_config


# Application parameter
class AppParam:
    def __init__(self):
        self.ulr = False
        self.end_date = ""
        self.start_date = ""
        self.help = False
        self.has_chart = False
        self.savemd = False
        self.loadmd = False
        self.hasBackTest = False
        self.feed = ""  # yahoo feeder
        self.pid = 1  # 0-dow30,1-zr focus list,2-jpm/zack list
        self.tick_df = pandas.DataFrame({}, columns=['symbol','exg','sina','goog','googexg'])
        self.sgy_param = {}
        self.verbose = 0
        self.tail_offset = 0
        self.symbol_lst_file = ""
        self.display = True
        self.chart_param = ""

    def reset_parames(self):
        self.__init__()

    def show_params(self):
        if self.display:
            print "%-20s: %-50s" % ("use", self.symbol_lst_file)
            print "%-20s: %-50s" % ("start date", self.start_date)
            print "%-20s: %-50s" % ("end date", self.end_date)
            print "%-20s: %-50s" % ("portfolio id mask ", self.pid)
            print "%-20s: %-50s" % ("use chart", self.has_chart)
            if self.has_chart:
                print "%-20s: %-50s" % ("chart param", self.chart_param)
            print "%-20s: %-50s" % ("load marketdata", self.loadmd)
            print "%-20s: %-50s" % ("save marketdata", self.savemd)
            print "%-20s: %-50s" % ("backtest", self.hasBackTest)
            print "%-20s: %-50s" % ("feeder", self.feed)
            print "%-20s: %-50s" % ("verbose", self.verbose)
            print "%-20s: %-50s" % ("use last result", self.ulr)
            print "...................."

class ms_paramparser:
    def __init__(self):
        # TODO move parse pid here later
        self.mtd = marketdata.MarketData()
        self.cfg = ms_config.MsDataCfg("")
        '''
        self.symbolLstFile = self.cfg.getDataConfig("marketdata")
        self.ulr = False
        self.initParams()
        '''
        self.app_param = AppParam()
        pass
    '''
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
    '''
    def get_parsed_opts(self):
        return self.opts

    # app_params = array(split)
    def parseOption(self, params, display=True):
        # self.initParams()
        self.app_param.reset_parames()

        try:
            opts, args = getopt.getopt(params, "v:f:t:s:e:i:g:c:h",
                ["filename", "ticklist", "startdate", "enddate", "pid", "strategy", "help", "chart", "savemd",
                 "loadmd", "uselastresult", "backtest", "feed=", "verbose", "tailoffset=", "buy=", "sell="])
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()

        self.opts = opts

        if display:
            print "%-20s:%-50s" % ("parameter dict", opts)
        for opt, arg in opts:
            if opt in ("-f", "--filename"):
                # self.symbolLstFile = arg
                self.app_param.symbol_lst_file = arg
            elif opt in ("-t", "--ticklist"):
                # self.tickdf = self.mtd.parseTickLstDf(arg)
                self.app_param.tick_df = self.mtd.parseTickLstDf(arg)
            elif opt in ("-s", "--startdate"):
                # self.startdate = arg
                self.app_param.start_date = arg
            elif opt in ("-e", "--enddate"):
                # self.enddate = arg
                self.app_param.end_date = arg
            elif opt in ("-i", "--pid"):
                idLst = arg.split(",")
                # self.pid = self.mtd.parsePidLst(idLst)
                self.app_param.pid = self.mtd.parsePidLst(idLst)
            elif opt in ("-g", "--strategy"):
                # self.sgyparam = self.parseStrategy(arg)
                self.app_param.sgy_param = self.parseStrategy(arg)
            elif opt in ("-h", "--help"):
                self.usage()
                # self.help=True
                self.app_param.help = True
            elif opt in ("-c", "--chart"):
                # self.haschart = True
                # self.chartparam = arg
                self.app_param.has_chart = True
                self.app_param.chart_param = arg

            elif opt in "--backtest":
                # self.hasBackTest = True
                self.app_param.hasBackTest = True
            elif opt in "--savemd":
                #self.savemd = True
                self.app_param.savemd = True
            elif opt in "--loadmd":
                # self.loadmd = True
                self.app_param.loadmd = True
            elif opt in "--feed":
                # self.feed = arg
                self.app_param.feed = arg
            elif opt in "--uselastresult":
                # self.ulr = True
                self.app_param.ulr = True
            elif opt in ("-v","--verbose"):
                # self.verbose = int(arg)
                self.app_param.verbose = int(arg)
            elif opt in "--tailoffset":
                # self.tailoffset = int(arg)
                self.app_param.tail_offset = int(arg)
            elif opt in "--buy":
                self.parseBuy(arg)
            elif opt in "--sell":
                self.parseSell(arg)

        if self.app_param.end_date == "":
            # self.enddate = datetime.datetime.now().strftime("%Y-%m-%d")
            self.app_param.end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        if not self.app_param.start_date:
            start_day = datetime.date.today() - datetime.timedelta(days=365)
            # self.startdate = startday.strftime("%Y-%m-%d")
            self.app_param.start_date = start_day.strftime("%Y-%m-%d")

        if self.app_param.symbol_lst_file == "":
            self.app_param.symbol_lst_file = self.cfg.getDataConfig("marketdata")

        '''
        if display:
            print "%-20s: %-50s" % ("use", self.symbolLstFile)
            print "%-20s: %-50s" % ("start date", self.startdate)
            print "%-20s: %-50s" % ("end date", self.enddate)
            print "%-20s: %-50s" % ("portfolio id mask ",self.pid)
            print "%-20s: %-50s" % ("use chart", self.haschart)
            if self.haschart:
                print "%-20s: %-50s" % ("chart param",self.chartparam)
            print "%-20s: %-50s" % ("load marketdata", self.loadmd)
            print "%-20s: %-50s" % ("save marketdata", self.savemd)
            print "%-20s: %-50s" % ("backtest", self.hasBackTest)
            print "%-20s: %-50s" % ("feeder", self.feed)
            print "%-20s: %-50s" % ("verbose", self.verbose)
            print "%-20s: %-50s" % ("use last result", self.ulr)
            print "...................."
        '''
        self.app_param.show_params()
        return self.app_param

    def parseBuy(self, arg):
        tokens = arg.split('&')
        #self.buydict = {key: 0 for key in tokens}
        self.app_param.buydict = {key: 0 for key in tokens}
        '''
        for item in tokens:
            order = item.split(':')
            if len(order)>1:
                self.buydict[order[0]] = int(order[1])
            else:
                self.buydict[order[0]] = 0
        '''

    def parseSell(self, arg):
        tokens = arg.split('&')
        # self.selldict = {key: 0 for key in tokens}
        self.app_param.selldict = {key: 0 for key in tokens}



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
    '''
    def getSymbolDf(self):
        print "ms_paramparser getSymbolDf, ERROR please move to MTD!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
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
    '''