'''
this is the main portal of conviction buy program

'''
#from ConfigParser import SafeConfigParser
import ConfigParser
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

class Console:
    _argdct = {"pid":"-i","feed":"--feed","savemd":"","loadmd":"--loadmd","strategy":"-g"}
    def __init__(self):
        self.configFile = "cb_config.cfg"
        self.cbparser = ConfigParser.ConfigParser()        
        #self.cbparser = ConfigParser.RawConfigParser(None, multidict)
        pass
        
    def process(self):
        print os.environ['zackfile']
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
            #cmdlst.append('marketscan.py')
            #print cmd
            #os.popen(cmd)

            #can work
            #print cmdlst
            #cmdlst.append(sys.executable)
            #subprocess.Popen(cmdlst)
            cmdstr = dct['cmd']
            print cmdstr
            process = subprocess.Popen("python "+cmdstr)                        
            
            #sys.argv = ['-g "ms_zack&%rank<=2" -i 1,2,3 --savemd']
            #sys.argv = cmdlst
            #exec(open("marketscan.py").read(), globals())

#            subprocess.Popen(['python','marketscan.py'],shell = True)
            
            #subprocess.call(['python test1.py'])
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
    obj = Console()
    obj.process()
 
 
 
 