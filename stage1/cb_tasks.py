'''
this is the main portal of conviction buy program

'''

#import os
import subprocess
#import sys
import marketscan
import ms_config

'''
class multidict(dict):
    _unique = 0

    def __setitem__(self, key, val):
        print "setitem",key,val
        if isinstance(val, dict) and key in self:
            #print key,val,"isinstance dict"
            self._unique += 1
            key += str(self._unique)
            #print "insert",key
        dict.__setitem__(self, key, val)
        #print "insert",key,val
'''

class CbTasks:
    #_argdct = {"pid":"-i","feed":"--feed","savemd":"","loadmd":"--loadmd","strategy":"-g"}
    def __init__(self):
        #self.configFile = "cb_config.cfg"
        #self.cbparser = ConfigParser.RawConfigParser()        
        #self.cbparser = ConfigParser.RawConfigParser(None, multidict)
        self.msconfig = ms_config.MsDataCfg("cb_task.cfg") #file name
        self.datacfg = ms_config.MsDataCfg("")
        pass
        
    def process(self):
        #save daily output filename
        output = "dailyreport_" + self.datacfg.getFileSurfix() + ".txt"
        self.datacfg.saveDataConfig('output_report',output)
        of = self.datacfg.getDataConfig("output_report")
        
        with open(of, "w") as myfile:
            myfile.write("===== Daily Report =====")
    
        
        for sect in self.msconfig.getSections():
            cmdstr = self.msconfig.getConfig(sect,'cmd')

            with open(of, "a") as reportfile:
                print >>reportfile, "\n\n[ ",sect," ]\n"
                print >>reportfile, cmdstr
                
            print sect
            print cmdstr
            if (cmdstr!=""):
                process = subprocess.Popen("python "+cmdstr)
                #wait until it complete?     
                process.wait()
                print('Finished process')               
            
        pass
 
                
if __name__ == "__main__":
    obj = CbTasks()
    obj.process()
 
 
 
 
 