class basestrategy:
    #def __init__(self):
        #self.initDeposit = initDeposit
    #    self.initDeposit = 0
    def setup(self,initDeposit):
        self.initDeposit = initDeposit        
    def procSingleData(self,price):
        return
        
    def procMultiData(self,priceLst):
        return
    def config(self,name,value):
        print "config",name,value                