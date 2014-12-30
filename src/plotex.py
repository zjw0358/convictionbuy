import pandas.io.data as web
import matplotlib.pyplot as plt
import pandas
import sys

def getStock(symbol):
    all_data = web.get_data_yahoo(symbol,'1/1/2012','12/20/2014')
    
    close_px = all_data['Adj Close'] 
    mavg = pandas.rolling_mean(close_px, 50)
    #print mavg
    all_data['mvg50'] = pandas.Series(mavg,index=all_data.index)
    print all_data
    validma50(all_data)
    drawChart(all_data)

def drawChart(data):
    print "drawChart"
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    data['Adj Close'].plot(ax=ax,style='k')
    data['mvg50'].plot(ax=ax,style='k--')

def validma50(data):
    #c1 = ((data['Low'] <= (data['mvg50']*1.005)).bool() and (data['Adj Close'] >= (data['mvg50']*1.001)).bool())
    sup = (data['Adj Close'] >= (data['mvg50']*1.001)) & (data['Low'] <= (data['mvg50']*1.005))
    #print sup
    sup2 = data[sup]
    print sup2.index
    #print supdata['Date']
    #c2 = (data['Adj Close'] >= (data['mvg50']*1.001))
    #print (c1)
    
    '''if (c1==True and c2==True):
        return True
    else:
        return False'''


getStock('gild')
'''print len(sys.argv)
if len(sys.argv)<2:
    sys.exit()

symbol=sys.argv[1]
print symbol
getStock(symbol)'''