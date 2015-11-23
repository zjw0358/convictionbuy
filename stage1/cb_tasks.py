'''
this is the main portal of conviction buy program

'''
import 
import os
import subprocess
import sys
import marketscan
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
    _argdct = {"pid":"-i","feed":"--feed","savemd":"","loadmd":"--loadmd","strategy":"-g"}
    def __init__(self):
        self.configFile = "cb_config.cfg"
        self.cbparser = ConfigParser.RawConfigParser()        
        #self.cbparser = ConfigParser.RawConfigParser(None, multidict)
        pass
    '''   
    def saveConfig(self):
        cbp = self.cbparser
        cbp.add_section('Section1')
        cbp.set('Section1', 'an_int', '15')
        cbp.set('Section1', 'a_bool', 'true')
        # Writing our configuration file to 'example.cfg'
        with open(self.configFile, 'wb') as configfile:
            cbp.write(configfile)
        pass
    '''
     
    def process0(self):
        #unable to pass environment variable between process
        #print os.environ['zackfile']
        #sys.exit()
        self.saveConfig()
        sys.exit()
        #config = ConfigParser.ConfigParser()
        cbp = self.cbparser
        cbp.read(self.configFile)
        #print cbp.sections()

        for sect in cbp.sections():
            cmdlst = ['python','marketscan.py']
            
            dct = cbp._sections[sect]
            for key in dct:
                if key in self._argdct:
                    line ="%s%s" % (self._argdct[key],dct[key])
                    cmdlst.append(line)
            cmdstr = dct['cmd']
            process = subprocess.Popen("python "+cmdstr)                        
            
            '''
            unable to import?
            sys.argv = cmdlst
            execfile('marketscan.py')
            '''
            #subprocess.call(cmdlst)
                    #print type(dct)
            #pid = cbp.get(sect,'pid')
            #print pid
            pass
        #print self.cbparser['task']['pid']

        pass
                
if __name__ == "__main__":
    obj = CbTasks()
    obj.process()
 
 
 
 