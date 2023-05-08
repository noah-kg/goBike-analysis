import pandas as pd
import numpy as np
import itables

import plotly.graph_objects as go

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
             .reset_index(drop=True))
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

    dfp['Late Night']    = dfp.iloc[:,0:3].sum(axis=1) #12-2a
    dfp['Early Morning'] = dfp.iloc[:,3:6].sum(axis=1) #2-5a
    dfp['Morning']       = dfp.iloc[:,6:13].sum(axis=1) #6a-12p
    dfp['Afternoon']     = dfp.iloc[:,13:18].sum(axis=1) #12-5p
    dfp['Evening']       = dfp.iloc[:,18:21].sum(axis=1) #5-8p
    dfp['Night']         = dfp.iloc[:,21:].sum(axis=1) #8-12a
    dfp.drop(columns=dfp.iloc[:,0:24], inplace=True)

    fig = go.Figure()
    for col in dfp.columns:
        fig.add_trace(go.Bar(
            x=dfp.index,
            y=dfp[col],
            customdata=[f'{col}']*len(dfp.index),
            name=f'{col}',
            hovertemplate="<b>%{x}</b><br>%{customdata} Rentals: %{y}",
            showlegend=True
        ))
    
    # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        width=1000,
        height=600,
        barmode='stack',
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title=None,
        margin=dict(l=85, r=85, t=95, b=45),        
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
    df["age_group"] = pd.cut(x=df['member_age'],
                             bins=[18,25,35,45,55,65,75,85,95,130], 
                             labels=["18-24","25-34","35-44","45-54","55-64","65-74","74-84","85-94","95+"])
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x = df[df['member_gender'] == 'Male']['age_group'], 
                               name='Male', 
                               hovertemplate="<b>%{x}</b><br>Rentals: %{y}"))
    fig.add_trace(go.Histogram(x = df[df['member_gender'] == 'Female']['age_group'], 
                               name='Female',
                               hovertemplate="<b>%{x}</b><br>Rentals: %{y}"))
    fig.add_trace(go.Histogram(x = df[df['member_gender'] == 'Other']['age_group'], 
                               name='Other',
                               hovertemplate="<b>%{x}</b><br>Rentals: %{y}"))
    
     # Styling
    title = f"{title}<br><sup>{sub}"
    fig.update_layout(
        title=dict(text=title, font=dict(size=30)),
        width=1000,
        height=600,
        barmode='stack',
        plot_bgcolor='#f0f0f0',
        paper_bgcolor='#f0f0f0',
        yaxis_title=None,
        xaxis_title=None,
        margin=dict(l=85, r=85, t=95, b=45),        
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