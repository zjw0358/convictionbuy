import numpy as np

def buycomm(trancost):
    comm = trancost * 0.0025 * 1.07 
    return comm
    
def sellcomm(trancost):
    comm = trancost*(0.0025+0.0000174)*1.07
    return comm

def getBuyPower(money):
    return money/(1+0.0025*1.07)

        
def basefacts(bm_returns,sgy_returns):
    covmat = np.cov(bm_returns,sgy_returns)

    beta = covmat[0,1]/covmat[1,1]
    alpha = np.mean(sgy_returns)-beta*np.mean(bm_returns)
    
    
    ypred = alpha + beta * bm_returns
    SS_res = np.sum(np.power(ypred-sgy_returns,2))
    SS_tot = covmat[0,0]*(len(bm_returns)-1) # SS_tot is sample_variance*(n-1)
    r_squared = 1. - SS_res/SS_tot
    # 5- year volatiity and 1-year momentum
    volatility = np.sqrt(covmat[0,0])
    momentum = np.prod(1+sgy_returns.tail(12).values) -1
    
    # annualize the numbers
    prd = 12. # used monthly returns; 12 periods to annualize
    alpha = alpha*prd
    volatility = volatility*np.sqrt(prd) 
    #print beta,alpha, r_squared, volatility, momentum      
    return dict({'alpha':alpha,'beta':beta,'volatility':volatility,'momentum':momentum})
