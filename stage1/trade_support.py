'''
trade support
'''

class TradeSupport:
    def getLastSignal(self,buysg,sellsg,indct,buykey,sellkey):
        buyidx = 100000
        for idx,sig in enumerate(buysg[::-1]):
            if (sig!=""):
                buyidx = idx
                break;
        sellidx = 100000
        for idx,sig in enumerate(sellsg[::-1]):
            if (sig!=""):
                sellidx = idx
                break;
        
        if (sellidx < buyidx):
            indct[sellkey] = int(sellidx)
            return sellidx,"sell"
        else:
            indct[buykey] = int(buyidx)
            return buyidx,"buy"
        

        