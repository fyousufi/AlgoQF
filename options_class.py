from math import *

##create function for an American call option price


def bscholes_call_modelprice(price,strike,time_mature,vol,r,):
    ##Calc price of American Call
    ##price is price of underlying stock or future or other asset
    ##strike is the strike price of option
    ##time to maturity is the days left until the option expires
    ##vol is simply the volatility calculated or obtained of the stock itself (not IMplied volatility which is calculated)

     d1 = (log(S/X)+(r+sigma*sigma/2.)*T)/(sigma*sqrt(T))
     d2 = d1-sigma*sqrt(T)
     return S*CND(d1)-X*exp(-r*T)*CND(d2)


def CND(X):
    (a1,a2,a3,a4,a5)=(0.31938153,-0.356563782,1.781477937,-1.821255978,1.330274429)
    L = abs(X)
    K=1.0/(1.0+0.2316419*L)
    w=1.0-1.0/sqrt(2*pi)*exp(-L*L/2.)*(a1*K+a2*K*K+a3*pow(K,3)+a4*pow(K,4)+a5*pow(K,5))
    if X<0:
        w = 1.0-w
    return w
