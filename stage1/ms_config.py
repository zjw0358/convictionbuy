import ConfigParser
import datetime

class MsDataCfg:
    def __init__(self,cfgFile=""):
        if (cfgFile == ""):
            self.sectName = "datafile"
            self.configFile = "cb_config.cfg"
        else:            
            self.sectName = "cbtask"
            self.configFile = cfgFile #"cb_task.cfg"
        self.cbparser = ConfigParser.SafeConfigParser()  
        self.cbparser.read(self.configFile)      
        pass
        
    def getSections(self):
        print self.cbparser.sections()
        return self.cbparser.sections()
        pass
        
    def getDataConfig(self,sectName,key,default=""):
        cbp = self.cbparser
        print cbp.sections()
        try:
            if sectName=="":
                sectName = self.sectName
            value = cbp.get(sectName, key)
        except:
            value = default
        return value
        
    def saveDataConfig(self,sectName, key,value):
        #print "save config file",key,value
        cbp = self.cbparser
        if (sectName  ==""):
            sectName = self.sectName
        cbp.set(sectName, key, value)
        # Writing our configuration file to 'example.cfg'
        with open(self.configFile, 'wb') as configfile:
            cbp.write(configfile)
            
    def getCsvFileSurfix(self):
        return datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'   
if __name__ == "__main__":
    obj = MsDataCfg()
    obj.saveConfig("zack","msdata_zack.csv")    