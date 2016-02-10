'''
trade support
'''

class TradeSupport:
    def getLastSignal(self,buysg,sellsg,indct,buykey,sellkey):
        buyidx = float('nan')
        for idx,sig in enumerate(buysg[::-1]):
            if (sig!=""):
                buyidx = idx
                break;
        sellidx = float('nan')
        for idx,sig in enumerate(sellsg[::-1]):
            if (sig!=""):
                #print idx,sig
                sellidx = idx
                break;
                
        indct[sellkey] = (sellidx)
        indct[buykey] = (buyidx)        
        '''
        if (sellidx < buyidx):
            indct[sellkey] = int(sellidx)
            return sellidx,"sell"
        else:
            indct[buykey] = int(buyidx)
            return buyidx,"buy"
        '''
        

        