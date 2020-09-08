import numpy as np
import pandas as pd
from scipy import optimize
from scipy import integrate

def fit_odeint(x, beta, gamma):
    return integrate.odeint(SIR_model_t, (S0,I0,R0),  t, args=(beta,gamma))[:,1]

def SIR_model_t(SIR,t,beta,gamma):
    '''
        S: susceptible population
        I: infected population
        R: Recovered population
        
        dS+dI+dR=0
        S+I+R=N
    
    '''
    
    S,I,R=SIR
    dS_dt=-beta*S*I/N0
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return dS_dt,dI_dt,dR_dt

pd_raw=pd.read_csv('../data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

#Sum up the total confirmed cases in each country
total_confirmed_in_country=pd.DataFrame()
for each in pd_raw['Country/Region'].copy().drop_duplicates():
    for col in range(4,pd_raw.shape[1]-1):
        total_confirmed_in_country.loc[col-4,each]=pd_raw[pd_raw['Country/Region']==each].iloc[:,col].sum()

#Store the simulation result
SIR_spread_model={}
SIR_idx={}

beta=0.7
gamma=0.1

#Calculate simulation
for each in pd_raw['Country/Region'].drop_duplicates():
    
    n = 0
    for n in range(35,200):
        if total_confirmed_in_country[each].iloc[n]>5:
            SIR_idx[each]=n
            break
            
    ydata=np.array(total_confirmed_in_country[each].iloc[SIR_idx[each]:])
    t=np.arange(len(ydata))
    
    I0=ydata[0]
    R0=0
    
    popt=[beta,gamma]
    
    
    for ord in range(3,11):
        N0=pow(10,ord)
        S0=N0-I0
        
        try:
            popt, pcov= optimize.curve_fit(fit_odeint, t, ydata)
        except:
            continue
        else:
            if (np.sqrt(np.diag(pcov))[0]<0.01) and (np.sqrt(np.diag(pcov))[1]<0.01) :
                break
        
    SIR_spread_model[each]=fit_odeint(t,*popt)
