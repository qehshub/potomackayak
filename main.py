import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import requests
import json
import streamlit as st


def get_lvl():
    re = requests.get("https://waterservices.usgs.gov/nwis/iv/?site=01646500&period=PT2H&format=json&variable=00065").text
    jsonData = json.loads(re)
    values = len(jsonData['value']['timeSeries'][0]['values'][0]['value']) - 1
    lvl = jsonData['value']['timeSeries'][0]['values'][0]['value'][values]['value']
    return lvl

level = get_lvl()
df = pd.read_csv('https://raw.githubusercontent.com/andGarc/potomackayak/dev/data/locations.csv')

def set_color(df, level):
    level = float(level)
    df['color'] = np.where((df['max'] < level), 'red', 
                      np.where((df['min'] > level), 'blue', 'green'))
    return df

df = set_color(df, level)

red = df[df.color == 'red']
blue = df[df.color == 'blue']
green = df[df.color == 'green']

fig = go.Figure()

fig.add_trace(go.Scattermapbox(
        lat=red.lat,
        lon=red.lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
            color='rgb(245, 66, 66)',
            opacity=0.7
        ),
        hoverinfo='name'
    ))

fig.add_trace(go.Scattermapbox(
        lat=blue.lat,
        lon=blue.lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
            color='rgb(0, 128, 255)',
            opacity=0.7
        ),
        hoverinfo='name'
    ))

fig.add_trace(go.Scattermapbox(
        lat=green.lat,
        lon=green.lon,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=8,
            color='rgb(66, 245, 123)',
            opacity=0.7
        ),
        hoverinfo='name'
    ))

fig.update_mapboxes(
    center=dict(lon=-77.241 , lat=38.987),
    zoom=12,
    style="white-bg",
    layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ]
)


st.title('Potomac Playspot Map')
st.write(f'Water level at Little Falls: {level} ft')

left_col, left_middle_col, righ_middle_col, right_col = st.beta_columns(4)

if left_col.button('All'):
    pass

if left_middle_col.button('Recommended'):
    pass

if righ_middle_col.button('High'):
    pass

if right_col.button('Low'):
    pass

st.plotly_chart(fig, use_container_width=True)