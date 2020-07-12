"""
Last update 06-13-20 at 3:00 pm
-- need to clean up date formatting and moving avg formats and table sorting
-- Need to integrate "my-date" into the reanges
"""

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import datetime
import pytz
import plotly as plt
import numpy as np
import dash_renderer

my_date = datetime.datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d")
my_date20=(datetime.datetime.now(pytz.timezone('US/Eastern'))-datetime.timedelta(days=20)).strftime("%Y-%m-%d")
print('The beginnind date is ', my_date20, 'and the ending date is ', my_date)
print('')

df = pd.read_csv\
    ('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
#state = ['Georgia']
#df = df[df['Province_State'].isin(state)]
#df.head(5)
#df.info()

"""# Dataset is now stored in a Pandas Dataframe"""

columns =['UID', 'iso2', 'iso3','FIPS', 'code3', 'Lat', 'Long_', 'Combined_Key', 'Country_Region']
df.drop(columns, inplace=True, axis=1)
Covid_dfa = df[df.Admin2 == "Forsyth" ]
Covid_df = Covid_dfa[Covid_dfa.Province_State=='Georgia']
"""#Sum across states if multiple states or counties"""
table = pd.pivot_table(Covid_df, index =['Admin2', 'Province_State'], aggfunc = np.sum)
County_df =pd.melt(Covid_df,  id_vars=["Province_State", "Admin2"],var_name="Date", value_name="Count")
#Covert Date string into a datetime object
County_df['When'] = pd.to_datetime(County_df['Date'])

"""# Calculate Daily Increase"""
County_df['Del'] = County_df['Count'] - County_df['Count'].shift(+1)

"""#Now calculate the moving average"""
County_df['MovAvg'] = (County_df.iloc[:,5].rolling(window=7).mean()).round(decimals=3)
County_df = County_df[['When','Del','Count','MovAvg','Admin2','Province_State']]
County_df = County_df[County_df.When > '03-15-2020']
"""Now create subset for the table"""
#TCovidsorted_df = County_df[County_df.When > '5/30/2020']
County_df.sort_values(by=['When'], ascending=False,inplace=True)
County_df.rename(columns={'Amin2':'County',
                          'Province_State':'State'}, inplace=True)
TCovidsorted_df = County_df[County_df.When > '5-30-2020']
TCovidsortedc_df = TCovidsorted_df.copy()
TCovidsortedc_df['When'] = TCovidsorted_df['When'].dt.strftime('%Y-%m-%d')
TCovidsortedc_df.rename(columns={'Del':'Daily Increase',
                                 'Count':'Cumulative_Total',
                                 'MovAvg':'7_Day_Moving_Avg',
                                 'Admin2':'County'}, inplace=True)
print(TCovidsortedc_df.columns)
"""Now read state data in preparation for plotting
________________________________________________________________________________________________"""
df = pd.read_csv(
    'https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv')
state = ['Georgia']
df = df[df['Province_State'].isin(state)]
columns = ['UID', 'Admin2', 'iso2', 'iso3', 'FIPS', 'code3', 'Lat', 'Long_', 'Combined_Key', 'Country_Region']
df.drop(columns, inplace=True, axis=1)
table = pd.pivot_table(df, index=['Province_State'], aggfunc=np.sum)

df = table.reset_index()

State_df = pd.melt(df, id_vars=["Province_State"], var_name="Date", value_name="Count")
#State_df.info()

State_df['When'] = pd.to_datetime(State_df['Date'])
State_df = State_df.sort_values(by=['When'])
State_df['Del'] = State_df['Count'] - State_df['Count'].shift(+1)

State_df['MovAvg'] = (State_df.iloc[:, 4].rolling(window=7).mean()).round(decimals=2)


print(my_date, "-", my_date20)
print(State_df.head(5))
State_df = State_df[State_df.When > '3/15/2020']
State_df.sort_values(by=['When'], inplace=True)

print("The current count for Georgia on ", State_df['When'].iloc[-1].strftime("%Y-%m-%d"), " is ", State_df['Count'].iloc[-1])
print('')
dfa = pd.read_csv('https://covidtracking.com/api/v1/states/daily.csv')
state = ['GA']
dfa = dfa[dfa['state'].isin(state)]

dfa['PercP'] = ((dfa['positive'] / dfa['total'])*100).round(decimals=2).astype(str).add('%')

dfa.loc[dfa['totalTestResultsIncrease'] < 0, 'totalTestResultsIncrease'] = 0
dfa['When'] = (pd.to_datetime(dfa['date'],format='%Y%m%d')).dt.strftime('%Y-%m-%d')

dfa=dfa[['When', 'positiveIncrease','deathIncrease', 'hospitalizedIncrease','death','hospitalized', 'total','positive','PercP','totalTestResultsIncrease']]
dfa.rename(columns={'hospitalizedIncrease':'HospInc',
                          'positiveIncrease':'PosInc',
                          'deathIncrease':'Deaths',
                           'PercP':'% Positive',
                          'totalTestResultsIncrease':'TestInc'
                        }, inplace=True)
"""=============================================================================================="""
app=dash.Dash()
app.title ="Georgia Covid"
app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
app.layout = html.Div(html.Div([
        html.Div([
                html.H1(children='A look at the Covid Cases in Georgia and Forsyth County',
                        style={'color' : 'blue', 'fontSize' : '14',
                            'textAlign': 'center',
                            'width': '200'},

                        className='twelve columns'),
                html.H3(children='Tables and Graphs showing the Forsyth County daily increase in cases',
                        style={'color' : 'blue',
                               'fontSize' : '14',
                            'textAlign': 'center'},
                        className='twelve columns'
                )
        ],
            className="row"
        ),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='New Cases',
                    figure={
                        'data': [
                            go.Scatter(
                                x=County_df.When,
                                y=County_df.MovAvg,
                                text=County_df.MovAvg,
                                mode=('lines+markers'),
                                line_shape='spline',
                                name='7 Day Moving Avg'
                            ),
                            go.Bar(
                                x=County_df.When,
                                y=County_df.Del,
                                text=County_df.Del,
                                name='Daily Increase',
                                textposition='outside',
                                marker={'color': 'lightgrey'}
                            )
                        ],
                        'layout': {
                            'title': 'Forsyth Daily Increase in Cases',
                            'pageborder': 'lightsteelblue',
                            'height': 800,
                            'texttemplate':'%{text:.0f}',
                            'legend': dict(
                                x=0.05,
                                y=0.9,
                                bgcolor = 'rgb(230, 200 230)',
                                borderwidth =1,
                                bordercolor='Black',
                                traceorder='normal',
                                font=dict(
                                    size=12, )
                            ),
                            'xaxis': dict(
                                title = 'Date',
                                tickangle = -45,
                                rangeselector=dict(
                                    buttons=list([
                                        dict(count=1,
                                             label="1m",
                                             step="month",
                                             stepmode="backward"),
                                        dict(step="all")
                                    ]),

                                ),
                                titlefont =dict(
                                    family='Arial',
                                    size=24,
                                    color='#7f7f7f'
                                ),
                                mirror=True,
                                ticks='outside',
                                type = 'date',
                                gridwidth = 2,
                                tickmode = 'linear',
#dtick = 172800000 = every other day
                                dtick = 172800000,
                                showline=True
#                                range=['2020-5-16', '2020-05-30']
                            )
                        }
                    }
                ),
            ], style={'marginTop':25, 'marginLeft':5},
                className= 'twelve columns',
            ),
            html.H3(children='''
                    The table below contains the data for Forsyth county
                ''',
                    style={'color': 'blue',
                           'fontSize': '14',
                           'textAlign': 'center'},
                    className='twelve columns'
                    ),
            html.Div([
                dash_table.DataTable(
                    id='table',
                    data=TCovidsortedc_df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in TCovidsortedc_df.columns],
                     style_data={'border': '1px solid black'},
                    style_header={
                        'backgroundColor': 'rgb(230, 200 230)',
                        'fontWeight': 'bold',
                        'fontSize': 14,
                        'border': '1px solid black',
                        'textAlign': 'center'
                    },
                    style_cell={
                         'fontSize': 14,
                        'font' : 'Arial',
#                        'height': 'auto',
                        # all three widths are needed
                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                        'whiteSpace': 'normal'
                    },
#                    style_cell_conditional=[
#                        {'if': {'column_id': 'When'},
#                         'width': '80px'},
 #                       {'if': {'column_id': 'Del'},
#                         'width': '80px'},
#                       {'if': {'column_id': 'MovAvg'},
#                         'width': '80px',
#                        'sorting': 'True' },
 #                       {'if': {'column_id': 'Count'},
 #                        'width': '80px'},
#                       {'if': {'column_id': 'State'},
#                         'width': '80px'},
#                       {'if': {'column_id': 'Admin2'},
#                         'width': '80px'}
#                    ],
#                    editable=True,
                    filter_action="native",
                    sort_action="native",
#                    sort_mode="multi",
#                    column_selectable="single",
#                    row_selectable="multi",
#                    row_deletable=True,
#                    selected_columns=[],
#                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_data_conditional = [
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_table={'overflowX': 'scroll',
                                'minWidth': '50%',
                                'maxwidth': '1200px'},
                ),
            ],
                style={'width': '1200px',
                    'textAlign': 'center',
                    'marginTop':25, 'marginLeft':50,
                       },
                className= 'eleven columns',
        ),
#            html.Hr(),

#            html.Hr(),
#            html.Hr(),
            html.Br(),
            html.Hr(),
                html.Div([
                dcc.Graph(
                    id='Forsyth Cumulative',
                    figure={
                        'data': [
                            go.Scatter(
                                x=County_df.When,
                                y=County_df.Count,
                                text=County_df.Count,
                                mode=('markers'),
                                name='Cumulative',
                                texttemplate = '%{text:.0f}'
                            )
                        ],
                    'layout': {
                        'xaxis': dict(
                            title='Date',
                            tickangle=-45,
                            rangeselector={'visible': True,
                                           'buttons': [{'step': 'all'},
                                                       {'step': 'month'},
                                                       ]},
                        ),
                            'title': 'Forsyth County Cumulative Cases'
                        }
                    }
                )
                ], className= 'twelve columns'
                ),
            html.Hr(),
            html.Div([
                dcc.Graph(
                    id='Georgia',
                    figure={
                        'data': [
                            go.Bar(
                                x=State_df.When,
                                y=State_df.Del,
                                text=State_df.Del,
                                name='Daily Increase',
                                texttemplate='%{text:.0f}',
                                textposition='outside',
                                marker={'color': 'lightgrey'}
                            ),

                            go.Scatter(
                                x=State_df.When,
                                y=State_df.MovAvg,
                                line_shape='spline',
                                mode=('lines+markers'),
                                name='7 day moving avg.',
                            )
                        ],
                    'layout': {
                            'height': 600,
                            'title': 'Georgia Cases',
                            'xaxis': dict(
                                title='Date',
                                tickangle=-45,
                                rangeselector={'visible': True, 'buttons': [{'step': 'all'}, {'step': 'week'}]},
                                titlefont=dict(
                                    family='Arial',
                                    size=24,
                                    color='#7f7f7f'),
#                                   rangeslider={'visible': True,
#                                   'min': '2020-05-01'},
                            ),
                            'texttemplate': '%{text:.0f}',
                            'legend': dict(
                                x=0.05,
                                y=0.9,
                                traceorder='normal',
                                font=dict(
                                    size=12, )
                            ),
                        }
                    }
                )
                ],
                className= 'twelve columns'
                ),
            html.Hr(),
            html.Br(),
            html.Hr(),
            html.H3(children='''
                The table below contains the data for Georgia
                    ''',
                    style={'color': 'blue',
                           'fontSize': '14',
                           'textAlign': 'center'},
                    className='twelve columns'
                    ),
            html.Div([
                dash_table.DataTable(
                    id='tablestate',
                    data=dfa.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in dfa.columns],
#                    style_as_list_view=True,
                    style_data={'border': '1px solid black'},
#                    title='test',
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold',
                        'border': '1px solid black',
                        'textAlign': 'center'
                    },
                    style_cell={
                        'fontSize': 14,
                        'font': 'Arial',
                        'minWidth': '80px', 'width': '80px', 'maxWidth': '80px',
                        'whiteSpace': 'normal'
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'When'},
                         'width': '80px'},
                    ],
#                    editable=True,
                    filter_action="native",
                    sort_action="native",
#                    sort_mode="multi",
#                    column_selectable="single",
#                    row_selectable="multi",
#                    row_deletable=True,
#                    selected_columns=[],
#                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=15,
                    style_data_conditional = [
                        {'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 228, 248)'}
                    ],
                    style_table={'overflowX': 'scroll',
                                'minWidth': '50%',
                                'maxwidth': '1200px'},
                ),
            ],
                style={'width': '1200px',
                    'textAlign': 'center',
 #                   'marginleft : '50',
                    'marginTop': '25'},
#
                className= 'eleven columns',
        ),

    ], className='twelve columns '),
        html.Div([
                dcc.Graph(
                    id='Georgia Daly Increase',
                    figure={
                        'data': [
                            go.Bar(
                                x=dfa.When,
                                y=dfa.HospInc,
                                text=dfa.HospInc,
                                name='Daily Increase in Hospitalizations',
                                texttemplate='%{text:.0f}',
                                textposition='outside',
                                marker={'color': 'lightgrey'}
                            ),

                            go.Scatter(
                               x=State_df.When,
                               y=State_df.MovAvg,
                               line_shape='spline',
                               mode=('lines+markers'),
                                name='Mov. Avg. Georgia Daily Increase.',
                            )
                        ],
                    'layout': {
                            'height': 600,
                            'title': 'Georgia Daily Hospitalizations Increase',
                            'xaxis': dict(
                                title='Date',
                                tickangle=-45,
                                rangeselector={'visible': True, 'buttons': [{'step': 'all'}, {'step': 'week'}]},
                                titlefont=dict(
                                    family='Arial',
                                    size=24,
                                    color='#7f7f7f'),
#                                   rangeslider={'visible': True,
#                                   'min': '2020-05-01'},
                            ),
                            'texttemplate': '%{text:.0f}',
                            'legend': dict(
                                x=0.05,
                                y=0.9,
                                traceorder='normal',
                                font=dict(
                                    size=12, )
                            ),
                        }
                    }
                )
                ],
                className= 'twelve columns'
                ),
        ], className="row"
        )
)

if __name__ == '__main__':
    app.run_server(debug=True)
print("Hello world")
