from marketscan import *
from ind_base_px import BaseIndPx
from st_pattern import StrategyPattern
from trade_support import TradeSupport


class sgy_br_ma50(BaseIndPx):
    def runIndicator(self, symbol, ohlc, param={}):
        st_sma = importStrategy("st_sma", symbol, ohlc)
        st_dmi = importStrategy("st_dmi", symbol, ohlc)
        dist50idx = ag50bidx = dmibidx = ma10bidx = ma50bidx = vol10bidx = -1
        spread = 6
        if 'dmi_buy' in st_dmi.ind:
            dmibidx = st_dmi.ind['dmi_buy']
        if 'ag50b' in st_sma.ind:
            ag50bidx = st_sma.ind['ag50b']
        if 'ma10b' in st_sma.ind:
            ma10bidx = st_sma.ind['ma10b']
        if 'ma50b' in st_sma.ind:
            ma50bidx = st_sma.ind['ma50b']
        if 'vol10b' in st_sma.ind:
            vol10bidx = st_sma.ind['vol10b']
        if 'dist50' in st_sma.ind:
            dist50idx = st_sma.ind['dist50']

        lst = [dmibidx, ag50bidx, ma10bidx, ma50bidx, vol10bidx, dist50idx ]
        #print lst
        def getminmaxv(lst):
            minv = 100000
            maxv = 0
            for item in lst:
                if item == -1:
                    return 0, 10000
                minv = min(item, minv)
                maxv = max(item, maxv)
            return minv, maxv

        minv, maxv = getminmaxv(lst)
        if (maxv - minv) <= spread:
            signal = "buy"
        else:
            signal = ""

        self.ind['brkout'] = signal
        self.ind['ma10b'] = ma10bidx
        self.ind['ma50b'] = ma50bidx
        self.ind['vol10b'] = vol10bidx
        self.ind['ag50b'] = ag50bidx
        self.ind['dmibuy'] = dmibidx
        self.ind['dist50'] = dist50idx
        #print symbol, "ma10b:", ma10bidx, "ma50b:", ma50bidx, "vol10b:", vol10bidx, "dmibuy:", dmibidx
        pass

    def runScan(self, df):
        df = df[df['brkout']=="buy"]
        return df, df.columns.values

