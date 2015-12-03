import ConfigParser
import datetime

class MsDataCfg:
    def __init__(self,cfgFile=""):
        if (cfgFile == ""):
            self.sectName = "datafile"
            self.configFile = "cb_config.cfg"
        else:            
            self.sectName = "cbtask" #ignore
            self.configFile = cfgFile #"cb_task.cfg"
        self.cbparser = ConfigParser.SafeConfigParser()  
        self.cbparser.read(self.configFile)      
        pass
        
    def getSections(self):
        print self.cbparser.sections()
        return self.cbparser.sections()
        pass
        
    def getConfig(self,sectName,key,default=""):
        cbp = self.cbparser
        #try:
        if sectName=="":
            sectName = self.sectName
        value = cbp.get(sectName, key)

        #except:
            #value = default
        print sectName,value
        return value
        
    def saveConfig(self,sectName, key,value):
        #print "save config file",key,value
        cbp = self.cbparser
        if (sectName  ==""):
            sectName = self.sectName
        cbp.set(sectName, key, value)
        # Writing our configuration file to 'example.cfg'
        with open(self.configFile, 'wb') as configfile:
            cbp.write(configfile)
            
    def getFileSurfix(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")
        
    #below are only for data config     
    #e.g. "[datafile] xx=yy
    def getDataConfig(self,key,default=""):
        cbp = self.cbparser
        sectName = self.sectName
        folder = ""
        #print "read",sectName,key
        #value = cbp.get(sectName, key)
        #print "read",sectName,value

        
        try:
            value = cbp.get(sectName, key)

            '''
            if (key=="folder"):
                return value
            else:
                folder = cbp.get(sectName, "folder")
                value = folder + value
            '''
        except:
            value = default
        
        return value

    def saveDataConfig(self,key,value):
        #print "save config file",key,value
        cbp = self.cbparser
        sectName = self.sectName
        cbp.set(sectName, key, value)
        with open(self.configFile, 'wb') as configfile:
            cbp.write(configfile)
            
            
if __name__ == "__main__":
    obj = MsDataCfg()
    obj.saveConfig("zack","msdata_zack.csv")    