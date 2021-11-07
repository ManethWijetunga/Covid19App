# W.L.P.M.Wijetunga
# Index-002

import pandas as pd
import numpy as np
import dash
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from IPython.display import HTML, display
from dash.dependencies import Input, Output, State

display(HTML("<style>.container { width:90% !important; }</style>"))

#Importing data set
chunksize=40000
covid = pd.read_csv('/Users/manethwijetunga/group_analytics/owid-covid-data.csv', chunksize=chunksize, iterator=True)

#Doing necessary changes to the dataset
q1_columns = ['date', 'total_cases', 'new_cases', 'new_deaths', 'total_deaths']
q1 = covid[covid.location == 'World'].loc[:, q1_columns]

q2_columns = ['location', 'date', 'total_cases',
              'new_cases', 'new_deaths', 'total_deaths']
world = covid[covid.location == 'World'].loc[:, q2_columns].set_index('date')


srilanka = covid[covid.location == 'Sri Lanka'].loc[:, q2_columns]
dummydata = pd.DataFrame({'date': pd.date_range(
    '2020-01-22', '2020-01-26', )}).astype(str)
srilanka = pd.concat([dummydata, srilanka]).replace(
    np.nan, 0).set_index('date')
srilanka = srilanka.drop('location', axis=1)
srilanka.insert(0, 'location', ['SL']*len(srilanka))
# sl

RestofTheWorld = world.iloc[:, 1:] - srilanka.iloc[:, 1:]
RestofTheWorld.insert(0, 'location', ['RestofTheWorld']*len(RestofTheWorld))
# RoW

saark_countries = ['Afghanistan', 'Bangladesh', 'Bhutan',
                   'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka']
saark = covid[covid.location.isin(saark_countries)].loc[:,q2_columns].groupby('date').sum()
saark.insert(0, 'location', ['SAARK']*len(saark))
# saark

asia = covid[covid.location == 'Asia'].loc[:, q2_columns].set_index('date')
# asia

q2 = pd.concat([srilanka, RestofTheWorld, saark, asia]).reset_index()
q2.date = pd.to_datetime(q2.date)

q3 = covid.loc[:, ['date', 'location']]
q3['test_to_detection'] = covid.new_tests/covid.new_cases
q3

q4 = covid.loc[:, ['date', 'location', 'new_cases', 'new_tests']]
q4

q5 = covid.loc[:, ['date', 'location', 'population', 'life_expectancy' ]]
q5['death_to_case'] = covid.total_deaths/covid.total_cases
q5


app = dash.Dash(__name__, assets_external_path='styling.css')

#Layout of the web app
app.layout = html.Div([
    html.H1(id='header', children=['COVID-19 Dashboard']),

    # Q1
    html.Div([
    html.Div([
        html.H2("Worldwide Changes"),
        dcc.Dropdown(id='q1-dropdown',
                     options=[{'label': i.replace('_', ' '), 'value': i}
                              for i in q1_columns[1:]],
                     value=q1_columns[1]),
        dcc.DatePickerRange(id='q1-datepickerrange',
                            start_date=q1.date.min(),
                            end_date=q1.date.max()),
        dcc.Graph(id='q1-graph')
    ], style={"border": "1px black solid", 'width': '44%', 'display': 'inline-block', 
              'padding':'2vh 2vw'}),

    #Q2
    html.Div([
        html.H2("Sri Lanka vs Worldwide Changes"),
        dcc.Dropdown(id='q2-variable-dropdown',
                     options=[
                         {'label': i.replace('_', ' '), 'value': i} for i in q2_columns[2:]],
                     value=q1_columns[1]),
        dcc.DatePickerRange(id='q2-datepickerrange',
                            start_date=q1.date.min(),
                            end_date=q1.date.max()),
        dcc.Checklist(id='q2-checklist',
                      options=[{'label': i, 'value': i}
                               for i in ['RoW', 'Asia', 'SAARK']],
                      value=['RoW']),
        dcc.Dropdown(id='q2-aggregate-dropdown',
                     options=[{'label': i, 'value': i} for i in [
                         'Daily', 'Weekly Average', 'Monthly Average', '7-day average', '14-day average']],
                     value='Daily'),
        dcc.Graph(id='q2-graph'),

    ], style={"border": "1px black solid", 'width': '44%', 'display': 'inline-block', 
              'padding':'2vh 2vw'})]),

    #Q3
    html.Div([
        html.H2("Test to Detection"),
        dcc.Dropdown(id='location',
                     options=[{'label': i, 'value': i}
                              for i in q3.location.unique()],
                     value='Sri Lanka'),
        dcc.DatePickerRange(id='q3-datepickerrange',
                            start_date=q3.date.min(),
                            end_date=q3.date.max()),
        dcc.Graph(id='q3-graph'),

    ], style={"border": "1px black solid", 'width': '90%', 
              'padding':'2vh 4vw'}),
    
    
    #Q4
    #Make it a scatter plot
    #Include the corelation between the variables
    html.Div([
    html.Div([
        html.H2("Tests vs New cases"),
        dcc.DatePickerRange(id='q4-datepickerrange',
                            start_date=q4.date.min(),
                            end_date=q4.date.max()),
        dcc.Graph(id='q4-graph'),
    ], style={"border": "1px black solid", 'width': '44%', 'display': 'inline-block', 
              'padding':'2vh 2vw'}),
    
    #Q5
    #Make it a relation between x=total_cases vs y=total_deaths
    html.Div([
        html.H2("Total cases to Total deaths"),
        dcc.Dropdown(id='location2',
                     options=[{'label': i, 'value': i}
                              for i in q5.location.unique()],
                     value='Sri Lanka'),
        dcc.DatePickerRange(id='q5-datepickerrange',
                            start_date=q5.date.min(),
                            end_date=q5.date.max()),
        dcc.Graph(id='q5-graph'),

    ], style={"border": "1px black solid", 'width': '44%', 'display': 'inline-block',
              'padding':'2vh 2vw'})]),
    

])
#Callback for q1
@app.callback(Output('q1-graph', 'figure'),
              Input('q1-dropdown', 'value'),
              Input('q1-datepickerrange', 'start_date'),
              Input('q1-datepickerrange', 'end_date'))

#Update function for graph 1
def update_q1_fig(variable, start_date, end_date):
    #Filtering the date range and creating graph
    fig = px.line(data_frame=q1[(q1.date >= start_date) & (q1.date <= end_date)],
                  x='date', y=variable, title="Worldwide Changes")
    fig.layout.title.x = 0.5
    #Axis labels
    fig.update_layout(xaxis_title='<b>Date</b>',yaxis_title=f'<b>{variable.replace("_", " ")}</b>')
    return fig


#Callback for q2 
@app.callback(Output('q2-graph', 'figure'),
              Input('q2-variable-dropdown', 'value'),
              Input('q2-datepickerrange', 'start_date'),
              Input('q2-datepickerrange', 'end_date'),
              Input('q2-checklist', 'value'),
              Input('q2-aggregate-dropdown', 'value'))

#Update function for graph 2
def update_q2_fig(variable, start_date, end_date, checklist, frequency):
    #Displaying the selected variables
    print(variable, start_date, end_date, checklist, frequency)
    #Filtering the date range
    dates_filtered = q2[(q2.date >= start_date) & (q2.date <= end_date)]  
    #Appending SL dataset
    checklist.append('SL')
    location_filtered = dates_filtered[dates_filtered.location.isin(checklist)]

    # filter the frequency
    if frequency == 'Daily':
        title = "Daily changes"
        df = location_filtered
    elif frequency == 'Weekly Average':
        title = "Weekly Average changes"
        df = location_filtered.groupby([pd.Grouper(key='date', freq='W'), 'location'], ).mean().reset_index()
    elif frequency == 'Monthly Average':
        title = "Monthly Average changes"
        df = location_filtered.groupby([pd.Grouper(key='date', freq='M'), 'location'], ).mean().reset_index()
    elif frequency == '7-day average':
        title = "7-day Average changes"
        df = location_filtered.groupby('location').rolling(7, on='date').mean().reset_index()
    elif frequency == '14-day average':
        title = "14-day Average changes"
        df = location_filtered.groupby('location').rolling(14, on='date').mean().reset_index()

    #Creating the graph
    fig = px.line(data_frame=df, x='date', y=variable, color='location',title=title)
    #Axis labels
    fig.update_layout(xaxis_title='<b>Date</b>',yaxis_title=f'<b>{variable.replace("_", " ")}</b>')
    fig.layout.title.x = 0.5
    return fig


#Callback for q3 
@app.callback(Output('q3-graph', 'figure'),
              Input('location', 'value'),
              Input('q3-datepickerrange', 'start_date'),
              Input('q3-datepickerrange', 'end_date'))

#Update function for graph 3
def update_q3_fig(location, start_date, end_date):
     #Filtering the date range and location
    df = q3[(q3.location == location) & (q3.date >= start_date) & (q3.date <= end_date)]
    #Creating the graph
    fig = px.line(df, x='date', y='test_to_detection',title='Test to detection ratio')
     #Axis labels
    fig.update_layout(xaxis_title='<b>Date</b>',yaxis_title=f'<b>Test to detection ratio</b>')
    fig.layout.title.x = 0.5
    return fig


#Callback for q4 and its update function
@app.callback(Output('q4-graph', 'figure'),
              Input('location', 'value'),
              Input('q4-datepickerrange', 'start_date'),
              Input('q4-datepickerrange', 'end_date'))

#Update function for graph 4 (Change the location to the required ones)
#Check this again
def update_q4_fig(location, start_date, end_date):
     #Filtering the date range and location
    df = q4[(q4.location == location) & (q4.date >= start_date) & (q4.date <= end_date)]
    cor = round(df[['new_tests', 'new_cases']].corr()['new_cases'][0], 2)
    #Creating the graph
    fig = px.scatter(df, x='new_tests', y='new_cases',title='Test to detection ratio')
     #Axis labels
    fig.update_layout(xaxis_title='<b>Date</b>',yaxis_title=f'<b>Test to detection ratio</b>')
    fig.layout.title.x = 0.5
    fig.add_annotation(x=max(df['new_tests']), y=max(df['new_cases']),
                        text="Correlation: {}".format(cor),
                        font=dict(
                            family="Courier New, monospace",
                            size=25,
                            color="#ff7f0e"
                        ),
                        showarrow=False,
                        arrowhead=1)
    return fig

#Callback for q5
@app.callback(Output('q5-graph', 'figure'),
              Input('location2', 'value'),
              Input('q5-datepickerrange', 'start_date'),
              Input('q5-datepickerrange', 'end_date'))

#Update function for graph 5
def update_q5_fig(location, start_date, end_date):
     #Filtering the date range and location
    df = q5[(q5.location == location) & (q5.date >= start_date) & (q5.date <= end_date)]
    
    #Creating the graph
    fig = px.bar(df, x='date', y='death_to_case',title='Death to case ratio', color='death_to_case',
                 hover_data=['population', 'life_expectancy'],)
    #Axis labels
    fig.update_layout(xaxis_title='<b>Date</b>',yaxis_title=f'<b>Death to case ratio</b>')
    fig.layout.title.x = 0.5
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
