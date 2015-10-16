'''
Base Indication class need price data
'''

from collections import OrderedDict

class BaseIndPx(object):
    def __init__(self):
        self.cleanup()
        
    def cleanup(self):
        #print "BaseIndPx cleanup"
        self.ind = OrderedDict()
        
    def getIndicators(self):
        return self.ind
        
    def needPriceData(self):
        return True

    def usage(self):
        return "This is Base indicator with Price data needed"
