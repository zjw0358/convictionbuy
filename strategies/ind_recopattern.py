'''
http://thepatternsite.com/patternz.html
'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.misc import derivative

from ind_base_px import BaseIndPx

def algoFunc(ohlc):
    length = len(ohlc)
    '''
    x = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,\
                16,17,18,19,20,21,22,23,24,25,26,27,28,29,30])
    y = np.array([2,5,7,9,10,13,16,18,21,22,21,20,19,18,\
                17,14,10,9,7,5,7,9,10,12,13,15,16,17,22,27])
    '''
    x = np.arange(1,length+1)
    y = np.array(ohlc['Adj Close'])
    print x,y
    # Simple interpolation of x and y    
    f = interp1d(x, y)
    x_fake = np.arange(1.1, length, 0.1)
    #print x_fake
    # derivative of y with respect to x
    df_dx = derivative(f, x_fake, dx=1e-6)
    
    # Plot
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    
    ax1.errorbar(x, y, fmt="o", color="blue", label='Input data')
    ax1.errorbar(x_fake, f(x_fake), color="green",label="Interpolated data", lw=2)
    ax1.set_xlabel("x")
    ax1.set_ylabel("y")
    
    ax2.errorbar(x_fake, df_dx, lw=2)
    ax2.errorbar(x_fake, np.array([0 for i in x_fake]), ls="--", lw=2)
    ax2.set_xlabel("x")
    ax2.set_ylabel("dy/dx")
    
    leg = ax1.legend(loc=2, numpoints=1,scatterpoints=1)
    leg.draw_frame(False)
    for i in df_dx:
        print i

class ind_recopattern(BaseIndPx):
    def runIndicator(self,symbol,ohlc,param={}):
        #print ohlc
        self.setupParam(param)     
        #self.close_px = ohlc['Adj Close']
        algoFunc(ohlc)     

