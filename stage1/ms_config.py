import ConfigParser
import datetime

class MsDataCfg:
    def __init__(self,section="",file=""):
        if (section==""):
            self.sectDataFile = "datafile"
            self.configFile = "cb_config.cfg"
        else:
            self.sectDataFile = "datafile"
            self.configFile = "cb_config.cfg"
        self.cbparser = ConfigParser.SafeConfigParser()  
        self.cbparser.read(self.configFile)      
        pass
   
    def getDataConfig(self,key,default=""):
        cbp = self.cbparser
        try:
            value = cbp.get(self.sectDataFile, key)
        except:
            value = default
        return value
        
    def saveDataConfig(self,key,value):
        print "save config file",key,value
        cbp = self.cbparser        
        cbp.set(self.sectDataFile, key, value)
        # Writing our configuration file to 'example.cfg'
        with open(self.configFile, 'wb') as configfile:
            cbp.write(configfile)
    def getCsvFileSurfix(self):
        return datetime.datetime.now().strftime("%Y-%m-%d") + '.csv'   
if __name__ == "__main__":
    obj = MsDataCfg()
    obj.saveConfig("zack","msdata_zack.csv")    