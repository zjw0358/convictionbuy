import traceback
import ms_config
import sys
import getopt
from collections import OrderedDict
import pandas
import cb_report
import re
import ms_paramparser


class cb_daemon:
    class Command:
        def __init__(self):
            self.modulestr=""
            self.funcstr=""
            self.descstr=""
            self.paramstr=""
            self.typestr=""
            self.title=""
            pass
            
    def __init__(self):
        self.msconfig = ms_config.MsDataCfg("cb_daemon.cfg")
        self.datacfg = ms_config.MsDataCfg("")
        #self.scaner = marketscan.MarketScan()
        #self.feeder = ms_feed.ms_feed()
        self.params = ms_paramparser.ms_paramparser()
        self.cmdlst = OrderedDict()
        #self.modulelst = {'marketscan.py':self.scaner,'ms_feed.py':self.feeder}
        self.moduledct = {}
        self.interactive = False
        self.report = cb_report.CbReport()
        self.loadConfig()
        self.typelst = ["download","load",""]
        self.globalsetting = ""
        #self.setting = {'verbose':'0','timer':'1'}
        #for key in self.setting:
        #    self.setting[key] = self.datacfg.getDataConfig(key,self.setting[key])
            
        self.internalcmd = {'list':(self.listCmd,"list task"),
        'help':(self.help,"help"),
        'exit':(self.exit,'exit program'),
        'runtype':(self.runtype,"run tasks by type"),
        'reload':(self.reload,'reload config'),
        'config':(self.config,'config running parameter')}
        
        pass
        
    def parseOption(self):
        params = sys.argv[1:]
        try:
            opts, args = getopt.getopt(params, "iw", \
                ["interactive"])
        except getopt.GetoptError:
            print "parse option error"
            sys.exit()
        for opt, arg in opts:
            if opt in ("-i", "--interactive"):
                self.interactive = True  
            elif opt in ("-w", "--interactive"):
                #self.windows = True
                self.report.initFont()
        if (self.interactive):
            print "Interactive Mode..."    

        pass

    def config(self, args=""):
        if (args!=""):
            self.globalsetting = " " + args
        print "global setting", self.globalsetting
        '''
        flag = False
        allsetting = args.split(',')
        for pair in allsetting:
            #print pair
            token = pair.split('=')
            if len(token)==2:
                key = token[0].strip()
                value = token[1].strip()
                #print key,value
                if (key in self.setting):
                    self.setting[key] = value                    
                    flag = True
            pass
            
        for key in self.setting:
            print key,"=",self.setting[key]
            #if (flag):
            #    self.datacfg.saveDataConfig(key,self.setting[key])        
        '''
        pass
        
    def reload(self):
        self.msconfig = ms_config.MsDataCfg("cb_daemon.cfg")
        self.cmdlst.clear()
        self.loadConfig()
        print "reload done"
        
    def loadConfig(self):
        #print self.msconfig.getSections()
        for sect in self.msconfig.getSections():
            cmd = cb_daemon.Command()
            cmd.modulestr = self.msconfig.getConfig(sect,'cmd')
            cmd.title = sect
            cmd.funcstr = self.msconfig.getConfig(sect,'func')
            cmd.paramstr = self.msconfig.getConfig(sect,'param')
            cmd.descstr = self.msconfig.getConfig(sect,'desc')#.encode('utf-8')
            cmd.typestr = self.msconfig.getConfig(sect,'type')#.encode('utf-8')            
            
            if (cmd.modulestr!=""):
                self.cmdlst[sect.lower()] = cmd            
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
            s = "%-20s - %-50s" % (command,cmd.descstr)
            print s
        pass
        
    def combinationTask(self,args):
        tasklst = args.split(',')
        print "combination task",tasklst
        for task in tasklst:
            if (task in self.cmdlst):
                self.runCmd(self.cmdlst[task])        
        pass
           
    def runCmd(self,cmd):
        try:
        #module = self.modulelst[cmd.modulestr]
            if (cmd.modulestr not in self.moduledct):
                module_meta = __import__(cmd.modulestr, globals(), locals(), [cmd.modulestr])
                c = getattr(module_meta, cmd.modulestr) 
                module = c() # construct module
                self.moduledct[cmd.modulestr] = module
            else:
                module = self.moduledct[cmd.modulestr]
            
            ptrfunc = getattr(module,cmd.funcstr) 
        except:
            print cmd.modulestr,"Not a valid func",cmd.funcstr
            return
            
        print "\nRunning[",cmd.title,"]",cmd.modulestr,cmd.funcstr
        arg = cmd.paramstr + self.globalsetting
        
        try:
            ret=ptrfunc(arg)
        except Exception as err:
            #traceback.print_tb(err.__traceback__)
            print(traceback.format_exc())
            sys.exit()
        

        #if (cmd.retstr=='table'):
        #    pass
        if (type(ret)==pandas.core.frame.DataFrame):
            self.report.addTable(cmd.title,cmd.descstr,ret)
            pass
    
    def runtype(self,param=""):
        print "run task by type",param        
        typelst=param.split()
        self.onetime(typelst)

    #not allow match funcstr only
    '''
    def findCmdOrFunc(self,arg):
        if (arg in self.cmdlst):
            return self.cmdlst[arg]  #download1h
        else:
            for cmd in self.cmdlst:                
                if arg == self.cmdlst[cmd].funcstr: #download func
                    return self.cmdlst[cmd]
        return None
    '''
     
    def flytask(self,cmdstr):
        pattern = "([\w\.]*) ([\d\D]*)"
        an = re.match(pattern,cmdstr)
        if an!=None:
            command = an.group(1)
            #cmd = self.findCmdOrFunc(command)
            if (command in self.cmdlst):
                cmd = self.cmdlst[command]
                newcmd = cb_daemon.Command()
                newparam = an.group(2)
                oldparam = cmd.paramstr
                
                opt1 = self.params.parseOption(newparam.split(),False)
                opt2 = self.params.parseOption(oldparam.split(),False)  
                opt1dict={}
                opt2dict={}
                for item1,item2 in opt1:
                    opt1dict[item1]=item2
                for item1,item2 in opt2:
                    opt2dict[item1]=item2
                opt2dict.update(opt1dict)

                #            for opt2dict
                mparam = ''.join(['%s %s ' % (key,value) for (key,value) in opt2dict.items()])
                #print mparam
                
                '''  
                print opt1
                print "======"
                print opt2
                opt1dict = {opt1[i]: opt1[i+1] for i in range(0, len(opt1), 2)}
                opt2dict = {opt2[i]: opt2[i+1] for i in range(0, len(opt2), 2)}
                
                opt2dict.update(opt1dict)
                print "======"
                print opt2dict
                '''                                             
                newcmd.modulestr = cmd.modulestr
                newcmd.title = "flytask"
                newcmd.funcstr = cmd.funcstr
                newcmd.paramstr = mparam
                self.runCmd(newcmd)                
                return True
            else:
                #internal command with param,e.g. runtype
                if command in self.internalcmd:
                    param = an.group(2)  
                    func,desc=self.internalcmd[command] 
                    func(param)                                                 
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
    def onetime(self,typelst):
        for cmd in self.cmdlst:
            task = self.cmdlst[cmd]
            if (task.typestr not in typelst):
                continue
            self.runCmd(task)
        self.report.printPdf()
        pass
                 
    def process(self):  
        self.parseOption()
        if (self.interactive):
            self.daemon()
        else:
            self.onetime(self.typelst)
                     
        

if __name__ == "__main__":
    obj = cb_daemon()
    obj.process()