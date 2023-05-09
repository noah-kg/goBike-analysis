import pandas as pd
import numpy as np
import os
import itables
import plotly.express as px
import plotly.graph_objects as go
import cufflinks as cf
import chart_studio.plotly as py
from plotly.offline import download_plotlyjs, init_notebook_mode
from itertools import cycle
init_notebook_mode(connected=True)
cf.go_offline()

# Remove unnecessary control items in figures (for Plotly)
config = {
    'modeBarButtonsToRemove': ['zoomIn', 'zoomOut', 'resetScale2d', 'select2d', 'lasso2d'],
    'responsive': True,
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png',  # one of png, svg, jpeg, webp
        'filename': 'ifsc-analysis',
        'scale': 1
      }
}

def show_table(df, col=0, srt="desc"):
    """
    Function to display an itable for the given dataframe.
    
    df: the dataframe to be displayed
    col: the col you want to sort on
    center: flag to determine whether or not to center the table (not working)
    srt: the sorting order
    """
    return itables.show(df,
                        classes="hover order-column dt-head-right dt-body-right",
                        maxBytes=1e5,
                        scrollY="400px",
                        scrollCollapse=True,
                        lengthMenu=[20, 50, 100],
                        order=[[col, srt]])

def calc_missing(df):
    missing = df.isnull().sum() / len(df)
    df_na = (pd.DataFrame({'column': df.columns, '%_missing': missing*100, '#_rows': missing*len(df)})         
             .sort_values('%_missing', ascending=False)
             .reset_index(drop=True)
             .round(2))
    return df_na[df_na['%_missing'] > 0]

def plot_month(df, title, sub):
    dfp = (df.groupby([df['start_time'].dt.month, df['start_time'].dt.hour])['duration_sec'].count()
           .unstack(0)
           .fillna(0)
           .T)    
    
    months = {
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    dfp.rename(months, inplace=True)

    dfp['Late Night']    = dfp.iloc[:,0:3].sum(axis=1) #12-2a    5    
    dfp['Night']         = dfp.iloc[:,21:24].sum(axis=1) #8-12a    0
    dfp['Evening']       = dfp.iloc[:,17:21].sum(axis=1) #5-8p   1
    dfp['Afternoon']     = dfp.iloc[:,12:17].sum(axis=1) #12-5p  2 
    dfp['Morning']       = dfp.iloc[:,6:12].sum(axis=1) #6a-12p  3 
    dfp['Early Morning'] = dfp.iloc[:,3:6].sum(axis=1) #2-5a     4 
    dfp.drop(columns=dfp.iloc[:,0:24], inplace=True)
    # dfp = dfp.iloc[:,[4,5,0,1,2,3]] # reorders columns for legend

    color_discrete_sequence=cycle(px.colors.sequential.Agsunset)
    
    fig = go.Figure()
    for col in dfp.columns:
        fig.add_trace(go.Bar(
            x=dfp.index,
            y=dfp[col],
            customdata=[f'{col}']*len(dfp.index),
            name=f'{col}',
            marker_color=next(color_discrete_sequence),
            hovertemplate="<b>%{x}</b><br>%{customdata} Rentals: %{y}",
            showlegend=True
        ))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.96,
                    xanchor="center",
                    x=0.5),
        width=1000,
        height=600,
        barmode='stack',
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title=None,
        margin=dict(l=45, r=45, t=95, b=45),        
        xaxis=dict(
            categoryorder='array',
            categoryarray= ['June', 'July', 'August', 'September', 'October', 'November', 'December'],
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            showticklabels=True,
            gridcolor='#cbcbcb'
        )
    )
    
    return fig.show(config=config)

def plot_gender_age(df, title, sub):
    df['member_age'] = df['start_time'].dt.year - df['member_birth_year']
    df = df[df['member_age'] <= 100] # removes outliers
    df["age_group"] = pd.cut(x=df['member_age'],
                             bins=[18,25,35,45,55,65,75,85,95,130], 
                             labels=["18-24","25-34","35-44","45-54","55-64","65-74","74-84","85-94","95+"])
    
    cols = ['Male', 'Female', 'Other']
    
    fig = go.Figure()
    for col in cols:
        fig.add_trace(go.Histogram(x = df[df['member_gender'] == col]['age_group'], name=col, 
                                   hovertemplate="<b>%{x}</b><br>Rentals: %{y}"))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.96,
                    xanchor="center",
                    x=0.5),
        width=1000,
        height=600,
        barmode='stack',
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title=None,
        margin=dict(l=45, r=45, t=95, b=45),        
        xaxis=dict(
            showline=True,
            linecolor='black',
            categoryorder='array',
            categoryarray= ["18-24","25-34","35-44","45-54","55-64","65-74","74-84","85-94","95+"]
        ),
        yaxis=dict(
            showticklabels=True,
            gridcolor='#cbcbcb'
        )
    )
    
    return fig.show(config=config)

def plot_age_v_ride(df, title, sub):
    fig = go.Figure(data=go.Scatter(x=df['member_age'], 
                                    y=df['avg_duration'], 
                                    mode='markers + lines',
                                    name='',
                                    marker=dict(
                                        size=12,                                        
                                        colorscale='Viridis', # one of plotly colorscales
                                        colorbar={"title": 'Minutes'},                                        
                                        showscale=True
                                    ),
                                    marker_color=df['avg_duration'],                                    
                                    hovertemplate="<b>Age: %{x}</b><br>Avg. Duration (min): %{y:.1f}",))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        width=1000,
        height=600,
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title="Age",
        margin=dict(l=45, r=45, t=95, b=45),        
        xaxis=dict(
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            showticklabels=True,
            gridcolor='#cbcbcb'
        )
    )
    
    return fig.show(config=config)

def comb_stations(df):
    stations_s = df[['start_station_latitude', 'start_station_longitude', 'start_station_name']].value_counts().to_frame(name="Count")
    stations_e = df[['end_station_latitude', 'end_station_longitude', 'end_station_name']].value_counts().to_frame(name="Count")

    stations_s['Station'] = 'Start'
    stations_e['Station'] = 'End'
    
    stations_s.reset_index(inplace=True)
    stations_s.rename({'start_station_latitude': 'latitude', 'start_station_longitude': 'longitude', 'start_station_name': 'Name'}, axis=1, inplace=True)
    
    stations_e.reset_index(inplace=True)
    stations_e.rename({'end_station_latitude': 'latitude', 'end_station_longitude': 'longitude', 'end_station_name': 'Name'}, axis=1, inplace=True)
    
    return pd.concat([stations_s, stations_e])

def plot_stations(df, title, sub):    
    # px.set_mapbox_access_token(os.getenv('MAPBOX_KEY'))
    center={'lat':37.793458, 'lon':-122.350951}
    fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', 
                            size="Count", color="Station", size_max=30, zoom=11, 
                            hover_name="Name", center=center)
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        legend=dict(yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01),
        mapbox_style="carto-positron",
        width=1000,
        height=600,
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title=None,
        margin=dict(l=45, r=45, t=95, b=45),        
        xaxis=dict(
            showline=True,
            linecolor='black'
        ),
        yaxis=dict(
            showticklabels=True,
            gridcolor='#cbcbcb'
        )
    )
    
    return fig.show(config=config)

def plot_corr(df, title, sub):
    fig = go.Figure(data=go.Heatmap(
                    x=df.columns,
                    y=df.columns,
                    z=df.corr()))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        width=1000,
        height=600,
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title=None,
        margin=dict(l=45, r=45, t=95, b=45),        
        xaxis=dict(
            showline=True,
            showticklabels=True,
            linecolor='black'
        ),
        yaxis=dict(
            autorange='reversed',
            showticklabels=True,
            gridcolor='#cbcbcb'
        )
    )
    
    return fig.show(config=config)