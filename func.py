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

def gen_layout(fig, title, title_size=30, legendy_anchor='bottom', legendx_anchor='center', 
               width=1000, height =600, plot_bg='#f0f0f0', paper_bg='#f0f0f0', 
               y_title=None, x_title=None, l_mar=45, r_mar=45, t_mar=95, b_mar=45, 
               x_showline=True, linecolor='black', y_labels=True, gridcolor='#cbcbcb', 
               barmode='group'):
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=title_size)),
        width=width,
        height=height,
        barmode=barmode,
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg,
        yaxis_title=y_title,
        xaxis_title=x_title,
        margin=dict(l=l_mar, r=r_mar, t=t_mar, b=b_mar),        
        xaxis=dict(
            showline=x_showline,
            linecolor=linecolor
        ),
        yaxis=dict(
            showticklabels=y_labels,
            gridcolor=gridcolor
        )
    )
    return fig

def plot_gender_dist(df, title, sub):    
    fig = go.Figure()
    for col in df.columns[1:]:
        fig.add_trace(go.Bar(
            x=['Customer', 'Subscriber'],
            y=df[col],
            customdata=[f'{col}'] * len(df),
            name=f'{col}',
            hovertemplate="<b>%{customdata} %{x}s:</b><br>%{y}<extra></extra>",
        ))
    
    title = f"{title}<br><sup>{sub}"
    fig = gen_layout(fig, title)
    fig.update_layout(
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.96,
                    xanchor="center",
                    x=0.5)
    )    
    return fig.show(config=config)

def plot_gender_age(df, title, sub):    
    cols = ['Male', 'Female', 'Other']
    
    fig = go.Figure()
    for col in cols:
        fig.add_trace(go.Histogram(x = df[df['member_gender'] == col]['age_group'], 
                                   name=col,
                                   customdata=[f'{col}'] * len(df),
                                   hovertemplate="<b>%{customdata}s %{x}</b><br>Rentals: %{y}<extra></extra>"))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig = gen_layout(fig, title, barmode='stack')
    fig.update_layout(
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.96,
                    xanchor="center",
                    x=0.5),
        xaxis=dict(
            categoryorder='array',
            categoryarray= ["18-24","25-34","35-44","45-54","55-64","65-74","74-84","85-94","95+"]
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
    fig = gen_layout(fig, title, x_title='Age')
    
    return fig.show(config=config)

def plot_gender_dur(df, title, sub):
    cols = ['Male', 'Female', 'Other']
    fig = go.Figure()
    for col in cols:
        fig.add_trace(go.Scatter(x=df[df['member_gender'] == col]['member_age'],
                                 y=df[df['member_gender'] == col]['avg_duration'], 
                                 mode='markers + lines',
                                 name=f'{col}',
                                 customdata=[f'{col}'] * len(df),
                                 marker=dict(
                                     size=8,
                                 ),
                                 hovertemplate="<b>%{x} y/o %{customdata}s:</b><br>Avg. Duration (min): %{y:.1f}<extra></extra>"))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig = gen_layout(fig, title, x_title='Age')
    fig.update_layout(
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.96,
                    xanchor="center",
                    x=0.5)
    )
    
    return fig.show(config=config)

def rename_months(df):
    months = {
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December'
    }
    return df.rename(months)

def plot_month(df, title, sub):
    df = rename_months(df)

    df['Late Night']    = df.iloc[:,0:3].sum(axis=1) #12-2a    5    
    df['Night']         = df.iloc[:,21:24].sum(axis=1) #8-12a    0
    df['Evening']       = df.iloc[:,17:21].sum(axis=1) #5-8p   1
    df['Afternoon']     = df.iloc[:,12:17].sum(axis=1) #12-5p  2 
    df['Morning']       = df.iloc[:,6:12].sum(axis=1) #6a-12p  3 
    df['Early Morning'] = df.iloc[:,3:6].sum(axis=1) #2-5a     4 
    df.drop(columns=df.iloc[:,0:24], inplace=True)

    color_discrete_sequence=cycle(px.colors.sequential.Agsunset)
    
    fig = go.Figure()
    for col in df.columns:
        fig.add_trace(go.Bar(
            x=df.index,
            y=df[col],
            customdata=[f'{col}']*len(df.index),
            name=f'{col}',
            marker_color=next(color_discrete_sequence),
            hovertemplate="<b>%{x}</b><br>%{customdata} Rentals: %{y}<extra></extra>",
            showlegend=True
        ))
    
    # Styling    
    title = f"{title}<br><sup>{sub}"
    fig = gen_layout(fig, title, barmode='stack')
    fig.update_layout(
        legend=dict(orientation="h",
                    yanchor="bottom",
                    y=0.96,
                    xanchor="center",
                    x=0.5),
        xaxis=dict(
            categoryorder='array',
            categoryarray= ['June', 'July', 'August', 'September', 'October', 'November', 'December']
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
    fig = gen_layout(fig, title)
    fig.update_layout(
        legend=dict(yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01),
        mapbox_style="carto-positron"
    )
    
    return fig.show(config=config)