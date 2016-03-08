'''
trade support
'''

class TradeSupport:
    def getLastSignal(self,buysg,sellsg,indct,buykey,sellkey):
        buyidx = float('nan')
        sellidx = float('nan')
        if buysg:
            for idx,sig in enumerate(buysg[::-1]):
                if (sig == "buy"):
                    buyidx = idx
                    break;
            indct[buykey] = (buyidx)

        if sellsg:
            for idx,sig in enumerate(sellsg[::-1]):
                if (sig == "sell"):
                    #print idx,sig
                    sellidx = idx
                    break;

            indct[sellkey] = (sellidx)

        return buyidx, sellidx