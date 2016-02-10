import marketscan
import ms_feed
import ms_config
import sys
import getopt
from collections import OrderedDict
import pandas
import cb_report
import re

class CbDaemon:
    class Command:
        def __init__(self):
            self.cmdstr=""
            self.funcstr=""
            self.descstr=""
            self.paramstr=""
            #self.retstr=""
            self.title=""
            pass
            
    def __init__(self):
        self.msconfig = ms_config.MsDataCfg("cb_daemon.cfg") #file name
        self.datacfg = ms_config.MsDataCfg("")
        self.scaner = marketscan.MarketScan()
        self.feeder = ms_feed.ms_feed()
        self.cmdlst = OrderedDict()
        self.modulelst = {'marketscan.py':self.scaner,'ms_feed.py':self.feeder}
        self.interactive = False
        self.report = cb_report.CbReport()
        self.loadConfig()
        self.internalcmd = {'list':(self.listCmd,"list task"),'help':(self.help,"help"),'exit':(self.exit,'exit program')}
        pass
        
    def parseOption(self):
        params = sys.argv[1:]
        try:
            opts, args = getopt.getopt(params, "i", \
                ["interactive"])
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
        for opt, arg in opts:
            if opt in ("-i", "--interactive"):
                self.interactive = True  
        if (self.interactive):
            print "Interactive Mode..."     

        pass
           
    def loadConfig(self):
        #print self.msconfig.getSections()
        for sect in self.msconfig.getSections():
            cmd = CbDaemon.Command()
            cmd.cmdstr = self.msconfig.getConfig(sect,'cmd')
            cmd.title = sect
            cmd.funcstr = self.msconfig.getConfig(sect,'func')
            cmd.paramstr = self.msconfig.getConfig(sect,'param')
            cmd.descstr = self.msconfig.getConfig(sect,'desc')#.encode('utf-8')
            #print cmd.descstr
            #print unicode(cmd.descstr,'utf-8')
            #print cmd.descstr.decode('utf-8')
            #print isinstance(cmd.descstr,unicode)
            #cmd.retstr = self.msconfig.getConfig(sect,'ret')
            if (cmd.cmdstr!=""):
                self.cmdlst[sect.lower()] = cmd
            #self.report.process(cmd.descstr)
            #sys.exit()

        #self.report.process(cmd.descstr)
        #sys.exit()
        pass
        
    def help(self):
        for key in self.internalcmd:
            func,desc=self.internalcmd[key]
            print key,"-",desc
        pass
        
    def exit(self):
        answer = raw_input("Are you sure to exit? (Y/N)")      
        if (answer.lower()[0]=="y"):
            sys.exit()
        
    def listCmd(self):
        #print "listCmd"
        for command in self.cmdlst:
            cmd = self.cmdlst[command]
            print command,"\t - ",cmd.descstr
        pass
        
    def runCmd(self,cmd):
        #cmd = self.cmdlst[cmdstr]
        #print cmd.funcstr
        #print cmd.funcstr
        try:
            module = self.modulelst[cmd.cmdstr]
            ptrfunc = getattr(module,cmd.funcstr) 
        except:
            print "Not a valid func",cmd.cmdstr,cmd.funcstr
            return
        ret=ptrfunc(cmd.paramstr)

        #if (cmd.retstr=='table'):
        #    pass
        if (type(ret)==pandas.core.frame.DataFrame):
            self.report.addTable(cmd.title,cmd.descstr,ret)
            pass
    
    def flytask(self,cmdstr):
        pattern = "([\w\.]*) ([\w]*) ([\d\D]*)"
        an = re.match(pattern,cmdstr)
        if an!=None:
            module = an.group(1)
            func = an.group(2)
            param = an.group(3)
            if (module!="" and func!="" and param!=""):
                cmd = CbDaemon.Command()
                cmd.cmdstr = module
                cmd.title = "flytask"
                cmd.funcstr = func
                cmd.paramstr = param
                self.runCmd(cmd)
                return True
        return False

    # interactive mode
    def daemon(self):
        while (True):
            print "\n========================\nEnter command:"
            inputstr = raw_input()
            inputlower = inputstr.lower()
            print "========================"
            if (inputlower in self.cmdlst):
                #print "you are typing",inputstr
                self.runCmd(self.cmdlst[inputstr])
            elif (inputlower in self.internalcmd):
                func,desc=self.internalcmd[inputstr]
                func()
            else:
                if not self.flytask(inputstr):
                    print "Not a valid command,exiting..."

        pass 
    #run once
    def onetime(self):
        for cmd in self.cmdlst:
            self.runCmd(self.cmdlst[cmd])
        self.report.printPdf()
        pass
                 
    def process(self):  
        self.parseOption()
        if (self.interactive):
            self.daemon()
        else:
            self.onetime()
                     
        

if __name__ == "__main__":
    obj = CbDaemon()
    obj.process()