'''
trade support
'''

class TradeSupport:
    def getLastSignal(self,buysg,sellsg):
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
        print buyidx,sellidx
        if (sellidx < buyidx):
            return sellidx,"sell"
        else:
            return buyidx,"buy"

        