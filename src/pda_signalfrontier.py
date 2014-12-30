# -*- coding: utf-8 -*-
import pandas.io.data as web
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

#names = ['AAPL', 'GOOG', 'MSFT', 'GS', 'MS', 'BAC', 'C']
names = ['AAPL','XOM','PG','JPM','PFE']
compound = lambda x : (1 + x).prod() - 1

#sharpe rate=[E(Rp)－Rf]/σp
daily_sr = lambda x: x.mean() / x.std()

def get_px(stock, start, end):
    return web.get_data_yahoo(stock, start, end)['Adj Close']

def calc_mom(price, lookback, lag):
    mom_ret = price.shift(lag).pct_change(lookback)
    ranks = mom_ret.rank(axis=1, ascending=False)
    demeaned = ranks - ranks.mean(axis=1)
    return demeaned / demeaned.std(axis=1)

def strat_sr(prices, lb, hold):
    # Compute portfolio weights
    freq = '%dB' % hold
    port = calc_mom(prices, lb, lag=1)
    daily_rets = prices.pct_change()
    # Compute portfolio returns
    port = port.shift(1).resample(freq, how='first')
    returns = daily_rets.resample(freq, how=compound)
    port_rets = (port * returns).sum(axis=1)
    return daily_sr(port_rets) * np.sqrt(252 / hold)

def heatmap(df, cmap=plt.cm.gray_r):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    axim = ax.imshow(df.values, cmap=cmap, interpolation='nearest')
    ax.set_xlabel(df.columns.name)
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_xticklabels(list(df.columns))
    ax.set_ylabel(df.index.name)
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_yticklabels(list(df.index))
    plt.colorbar(axim)
    plt.show()

px = pd.DataFrame({n: get_px(n, '12/2/2012', '12/28/2014') for n in names})
px = px.asfreq('B').fillna(method='pad')
rets = px.pct_change()

'''print rets
print px
print (1 + rets).cumprod()
fig = plt.figure(facecolor='white')
(1 + rets).cumprod() - 1).plot()'''

lookbacks = range(20, 90, 5)
holdings = range(20, 90, 5)
dd = defaultdict(dict)
for lb in lookbacks:
    for hold in holdings:
        dd[lb][hold] = strat_sr(px, lb, hold)
    
ddf = pd.DataFrame(dd)
ddf.index.name = 'Holding Period'
ddf.columns.name = 'Lookback Period'
print ddf
heatmap(ddf)
