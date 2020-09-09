# %load ../src/visualization/visualize.py
import pandas as pd
import numpy as np

import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go

import os
print(os.getcwd())

df_input_large=pd.read_csv('../data/processed/COVID_final_set.csv', sep=';')


fig=go.Figure()

app=dash.Dash()
app.layout=html.Div([

    dcc.Markdown('''
    ## Applied Data Science on COVID-19 data

    This project is aim to show the data of confirmed cases and the doubling rates 
    in different country. This project was worked by applying a cross industry standard process,
    it covers the full walkthrough of: automated data gathering, data transformations,
    filtering and machine learning to approximating the doubling time, and (static) deployment of responsive dashboard.

    '''),
    
     dcc.Markdown('''
    ## Multi_Select Country for visualization
                  '''),
    
    dcc.Dropdown(
        id='country_drop_down',
        options=[{'label':each, 'value':each} for each in df_input_large['country'].unique()],
        value=['US','Georgia'], #pre-selected
        multi=True
    ),

    dcc.Markdown('''
    ## Select Timeline of confirmed COVID-19 cases on different topics
                 '''),
    
    dcc.Dropdown(
        id='doubling_time',
        options=[
            {'label':'Timeline Confirmed','value':'confirmed'},
            {'label':'Timeline Confirmed Filtered','value':'confirmed_filtered'},
            {'label':'Timeline Doubling Rate','value':'confirmed_DR'},
            {'label':'Timeline Doubling Rate Filtered','value':'confirmed_filtered_DR'},
            {'label':'SIR Virus Spread Model','value':'SIR_spread_model'}
        ],
        value='confirmed', #pre-selected
        multi=False
    ),

    dcc.Graph(figure=fig, id='main_window_slope')
    ])

@app.callback(
    Output('main_window_slope','figure'),
    [Input('country_drop_down','value'),
     Input('doubling_time','value')])

def update_figure(country_list,show_doubling):

    if'DR'in show_doubling:
        my_yaxis={
            'type':'log',
            'title':'Approximated doubling rate over 3 days, log-scale'
            }
    else:
        my_yaxis={
            'type':'log',
            'title':'Confirmed infected people (source johns hopkins csse, log-scale)'
            }
        
    if 'SIR_spread_model' in show_doubling:
        my_yaxis={
            'type':'log',
            'title':'True confirmed cases and corresponding simulation curve, log-scale'
            }

    traces=[]
    
    for each in country_list:

        df_plot=df_input_large[df_input_large['country']==each]

        if show_doubling=='doubling_rate_filtered':
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.mean).reset_index()
        else:
            df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.sum).reset_index()

        
        if show_doubling=='SIR_spread_model':
            
            df_plot[show_doubling]=np.append(np.zeros(SIR_idx[each]+1),total_confirmed_in_country[each][SIR_idx[each]:])
            df_plot[show_doubling][0:SIR_idx[each]+1]=np.nan

            traces.append(dict(
                        x=df_plot.date[SIR_idx[each]:],
                        y=SIR_spread_model[each],
                        mode='lines',
                        opacity=1,
                        #line_width=2,
                        #marker_size=2,
                        name=each+'_simulation')

                      )

        traces.append(dict(
            x=df_plot.date,
            y=df_plot[show_doubling],
            mode='markers+lines',
            opacity=0.6,
            #line_width=2,
            #marker_size=2,
            name=each)

            )



    return{

        'data':traces,
        'layout':dict(
            width=1280,
            height=720,
            xaxis={
                'title':'Timeline',
                'tickangle':-45,
                'nticks':20,
                'tickfont':dict(size=14,color='#7f7f7f')},
            yaxis=my_yaxis
            )
        
        }

if __name__=='__main__':
    app.run_server(debug=True,use_reloader=False)
