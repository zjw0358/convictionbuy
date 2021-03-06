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
    class Task:
        def __init__(self):
            self.module_str = ""
            self.func_str = ""
            self.desc_str = ""
            self.param_str = ""
            self.config_str =""
            self.type_str = ""
            self.title = ""
            pass
            
    def __init__(self):
        self.sgyfile = "cb_daemon.cfg"
        self.msconfig = ms_config.MsDataCfg(self.sgyfile)
        self.datacfg = ms_config.MsDataCfg("")
        self.param_parser = ms_paramparser.ms_paramparser()
        self.task_lst = OrderedDict()

        self.module_dct = {'cb_daemon': self}  # must initial the dct with self, otherwise will create duplication
        self.interactive = False
        self.report = cb_report.CbReport()
        self.load_task_config()
        self.typelst = ["download", "load", ""]
        self.global_setting = ""

        self.internalcmd = {'list': (self.listCmd, 'list task'),
                            'help': (self.help, 'help'),
                            'exit': (self.exit, 'exit program'),
                            'runtype': (self.runtype, 'run tasks by type'),
                            'reload': (self.reload, 'reload config'),
                            'config': (self.config, 'config running parameter')}
        
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

    def reload(self, filename=""):
        if filename != "":
            self.sgyfile = filename
        self.msconfig = ms_config.MsDataCfg(self.sgyfile)
        self.task_lst.clear()
        self.load_task_config()
        print "reload done"

    # load task config file
    def load_task_config(self):
        for sect in self.msconfig.getSections():
            task = cb_daemon.Task()
            task.module_str = self.msconfig.getConfig(sect, 'module')
            task.title = sect
            task.func_str = self.msconfig.getConfig(sect, 'func')
            task.param_str = self.msconfig.getConfig(sect, 'param')
            task.config_str = self.msconfig.getConfig(sect, 'config')
            task.desc_str = self.msconfig.getConfig(sect, 'desc')  # .encode('utf-8')
            task.type_str = self.msconfig.getConfig(sect, 'type')  # .encode('utf-8')
            
            if task.module_str != "":
                self.task_lst[sect.lower()] = task
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
        for command in self.task_lst:
            cmd = self.task_lst[command]
            s = "%-20s - %-50s" % (command,cmd.descstr)
            print s
        pass


    def config(self, args=""):
        if args != "":
            self.global_setting = " " + args
        print "change global setting to ", self.global_setting

    # combine task, use the previous out as the input
    def combination_task(self, args):
        t_lst = args.split(',')

        for t in t_lst:
            task = t.lower().strip()
            # print self, task, task in self.task_lst  # , self.task_lst.keys()
            if task in self.task_lst:
                print "\nCombination sub task=", task
                # print self.task_lst[task]
                self.run_task(self.task_lst[task])
        pass

    '''
       run a command
    '''
    def run_task(self, task):
        # print "check in run_task", task.title, "global", self.global_setting
        try:
            if task.module_str not in self.module_dct:  # create module on the fly
                module_meta = __import__(task.module_str, globals(), locals(), [task.module_str])
                c = getattr(module_meta, task.module_str)
                module = c()  # construct module
                self.module_dct[task.module_str] = module
                print "create module", task.module_str
            else:
                module = self.module_dct[task.module_str]

            ptr_func = getattr(module, task.func_str)
        except:
            # print(traceback.format_exc())
            print task.module_str, "Not a valid func", task.func_str
            return
            
        print "\nRunning[", task.title, "]", "module=", task.module_str, "func=", task.func_str

        if task.config_str != "":
            # print "task.config_str", task.config_str
            self.config(task.config_str)  # set config parameter

        param = task.param_str
        # print "self.global_setting", self.global_setting
        try:
            if task.func_str != "combination_task":  # normal task
                param += self.global_setting
            # print "run task", task.func_str, "param", param
            ret = ptr_func(param)
        except Exception as err:
            # traceback.print_tb(err.__traceback__)
            print(traceback.format_exc())
            sys.exit()

        if type(ret) == pandas.core.frame.DataFrame:
            self.report.addTable(task.title, task.desc_str, ret)
            pass
    
    def runtype(self,param=""):
        print "run task by type",param        
        typelst=param.split()
        self.onetime(typelst)

    #not allow match func_str only
    '''
    def findCmdOrFunc(self,arg):
        if (arg in self.task_lst):
            return self.task_lst[arg]  #download1h
        else:
            for cmd in self.task_lst:
                if arg == self.task_lst[cmd].func_str: #download func
                    return self.task_lst[cmd]
        return None
    '''

    '''
    dynamic running task
    '''
    def flytask(self, cmdstr):
        pattern = "([\w\.]*) ([\d\D]*)"
        an = re.match(pattern,cmdstr)
        if an is not None:
            command = an.group(1)
            # cmd = self.findCmdOrFunc(command)
            if command in self.task_lst:
                cmd = self.task_lst[command]
                newcmd = cb_daemon.Task()
                newparam = an.group(2)
                oldparam = cmd.param_str
                
                self.param_parser.parseOption(newparam.split(), False)
                opt1 = self.param_parser.get_parsed_opts()
                self.param_parser.parseOption(oldparam.split(), False)
                opt2 = self.param_parser.get_parsed_opts()
                opt1dict = {}
                opt2dict = {}
                for item1, item2 in opt1:
                    opt1dict[item1] = item2
                for item1, item2 in opt2:
                    opt2dict[item1] = item2
                opt2dict.update(opt1dict)

                # for opt2dict
                mparam = ''.join(['%s %s ' % (key,value) for (key,value) in opt2dict.items()])
                
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
                newcmd.module_str = cmd.module_str
                newcmd.title = "flytask"
                newcmd.func_str = cmd.func_str
                newcmd.param_str = mparam
                self.run_task(newcmd)
                return True
            else:
                # internal command with param,e.g. runtype
                if command in self.internalcmd:
                    param = an.group(2)  
                    func, desc = self.internalcmd[command]
                    func(param)                                                 
                    return True
        return False

    # interactive mode
    def daemon(self):
        while True:
            print "\n========================\nEnter command:"
            input_str = raw_input()
            input_lower = input_str.lower()
            print "========================"
            if input_lower in self.task_lst:  # task
                # print "you are typing", input_str
                self.run_task(self.task_lst[input_str])
            elif input_lower in self.internalcmd:
                func, desc = self.internalcmd[input_str]
                func()
            else:
                if not self.flytask(input_str):
                    print "Not a valid command,exiting..."

        pass 
    # run once
    def onetime(self,typelst):
        for cmd in self.task_lst:
            task = self.task_lst[cmd]
            if (task.typestr not in typelst):
                continue
            self.run_task(task)
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