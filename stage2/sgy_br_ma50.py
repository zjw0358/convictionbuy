from marketscan import *
from ind_base_px import BaseIndPx
import math
from st_pattern import StrategyPattern
from trade_support import TradeSupport


class sgy_br_ma50(BaseIndPx):
    def _combineSignal(self, ohlc, buydct, selldct):
        flag = True
        for key in buydct:
            if key not in ohlc:
                flag = False

        for key in selldct:
            if key not in ohlc:
                flag = False

        if (not flag):
            ohlc['signal'] = ['']*len(ohlc)
            return

        def cleardct(dct):
            for key in dct:
                dct[key] = 0
            pass


        def buyspread(dct):
            minv = 100000
            maxv = 0
            spread = 6
            for key in dct:
                minv = min(dct[key], minv)
                maxv = max(dct[key], maxv)
            if (maxv-minv) > spread:
                return False
            else:
                return True
            pass

        #print buydct,selldct
        cleardct(buydct)
        cleardct(selldct)

        signallst = []
        idx = 1
        for row_index, row in ohlc.iterrows():
            signal = ""
            for bs in buydct:
                if row[bs] == "buy":
                    buydct[bs] = idx

            for ss in selldct:
                if row[ss] == "sell":
                    selldct[ss] = 1

            buy_flag = True
            for bs in buydct:
                if buydct[bs] == 0:
                    buy_flag = False


            all_sell_flag = True
            one_sell_flag = False
            for ss in selldct:
                if selldct[ss] != 1:
                    all_sell_flag = False
                else:
                    one_sell_flag = True

            if one_sell_flag:
                # reset buydict
                buy_flag = False
                for bs in buydct:
                    buydct[bs] = 0

            if one_sell_flag:
                signal = "sell"
                for ss in selldct:
                    selldct[ss] = 0

            if buy_flag:
                if buyspread(buydct):
                    signal = "buy"
                for key in buydct:
                    buydct[key] = 0
            idx += 1
            signallst.append(signal)
        ohlc['brkout'] = signallst


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
        '''
        if 'dist200' in st_sma.ind:
            dist200idx = st_sma.ind['dist200']
        '''

        lst = [dmibidx, ag50bidx, ma10bidx, ma50bidx, vol10bidx, dist50idx ]
        #print lst
        def getminmaxv(lst):
            minv = 100000
            maxv = 0
            for item in lst:
                if item == -1 or math.isnan(item):
                    return 0, 10000
                minv = min(item, minv)
                maxv = max(item, maxv)
                #print item,minv,maxv
            return minv, maxv

        minv, maxv = getminmaxv(lst)
        if (maxv - minv) <= spread:
            signal = "buy"
        else:
            signal = ""
        #print symbol, signal,minv,maxv, lst
        self.ind['brkout'] = signal
        self.ind['ma10b'] = ma10bidx
        self.ind['ma50b'] = ma50bidx
        self.ind['vol10b'] = vol10bidx
        self.ind['ag50b'] = ag50bidx
        self.ind['dmibuy'] = dmibidx
        #self.ind['dist200'] = dist200idx
        self.ind['dist50'] = dist50idx

        #print symbol, "ma10b:", ma10bidx, "ma50b:", ma50bidx, "vol10b:", vol10bidx, "dmibuy:", dmibidx

        buydct = {'dmibuy':0, 'ag50b':0, 'ma10b':0, 'ma50b':0, 'vol10b':0, 'dist50':0}
        selldct = {'ma10s':0, 'ma50s':0, 'ma1050s':0, 'dmisell':0}
        self._combineSignal(ohlc, buydct, selldct)
        pass

    def runScan(self, df):
        df = df[df['brkout']=="buy"]
        return df, df.columns.values

