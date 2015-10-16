
class StrategyPattern(object):
    def __init__(self):
        pass
        
    def initData(self,fast,slow,offset):
        self.fast = fast
        self.slow = slow
        self.offset = offset
        pass
        
    def crossAbove(self):
        prevFast = self.fast[-self.offset]
        prevSlow = self.slow[-self.offset]
        signal = 65535 #float('nan')
        for idx, curSlow in enumerate(self.slow[-self.offset:]):
            #idx,-offset+idx
            currentFast = self.fast[-self.offset+idx]
            #print prevSlow,curSlow,prevFast,currentFast
            if (prevFast < prevSlow) and (currentFast > curSlow) :
                #signal = "True(%d)" % (self.offset-idx)
                signal = self.offset-idx
                #print "(buy)"
                # TODO
                #if (curSlow > prevSlow):
                #    signal += "*"
                #    print "****** strong signal********",signal
            prevFast = currentFast
            prevSlow = curSlow
        return signal
        
    def crossBelow(self):
        prevFast = self.fast[-self.offset]
        prevSlow = self.slow[-self.offset]
        signal = 65535 #float('nan')
        for idx, curSlow in enumerate(self.slow[-self.offset:]):
            #print idx,-offset+idx
            currentFast = self.fast[-self.offset+idx]
            if (prevFast > prevSlow) and (currentFast < curSlow):                
                #signal = "True(%d)" % (self.offset-idx)
                signal = self.offset-idx
            prevFast = currentFast
            prevSlow = curSlow
        return signal
