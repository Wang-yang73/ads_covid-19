%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='darkgrid')
mpl.rcParams['figure.figsize']=(16,9)

pd_raw=pd.read_csv('../data/raw/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
time_idx=pd_raw.columns[4:]
df_Spain=pd.DataFrame({'date':time_idx})
df_Spain['number']=np.array(pd_raw[pd_raw['Country/Region']=='Spain'].iloc[:,4:].sum(axis=0))

def SIR_model(SIR,beta,gamma):
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
    return([dS_dt,dI_dt,dR_dt])


t_initial=10
t_intro_measures=28
t_hold=90
t_relax=67

beta_max=0.55
beta_min=0.115
gamma=0.1

ydata = np.array(df_Spain.number[35:230])
t=np.arange(len(ydata))

N0=16000000
I0=ydata[0]
S0=N0-I0
R0=0

pd_beta=np.concatenate((np.array(t_initial*[beta_max]),
                        np.linspace(beta_max,beta_min,t_intro_measures),
                        np.array(t_hold*[beta_min]),
                        np.linspace(beta_min,beta_min+0.05,t_relax),
                       ))


SIR=np.array([S0,I0,R0])
propagation_rates=pd.DataFrame(columns={
    'susceptible':S0,
    'infected':I0,
    'recovered':R0
})

for each_beta in pd_beta:
    new_delta_vec=SIR_model(SIR,each_beta,gamma)
    SIR=SIR+new_delta_vec
    propagation_rates=propagation_rates.append({
    'susceptible':SIR[0],
    'infected':SIR[1],
    'recovered':SIR[2]},
    ignore_index=True
    )

fig, axl = plt.subplots(1,1)

axl.plot(propagation_rates.index,propagation_rates.infected,label='infected simulation',linewidth=3)

axl.bar(np.arange(len(ydata)),ydata,width=0.8,label='current infected Spain',color='r')
axl.set_ylim(10,2.5*max(propagation_rates.infected))
axl.set_yscale('log')
axl.set_title('Szenario SIR simulations')
axl.set_xlabel('time in days', size=16)
axl.legend(loc='best',prop={'size':16})
