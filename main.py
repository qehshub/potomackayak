import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import requests
import json
import streamlit as st
import pydeck as pdk
from PIL import Image


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

layers = [
        # above 
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'blue'],
        get_position='[lon,lat]',
        get_color='[0, 128, 255]',
        get_radius=50,
        pickable=True,),

        # below
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'red'],
        get_position='[lon,lat]',
        get_color='[245, 66, 66]',
        get_radius=50,
        pickable=True,),

        # just right
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'green'],
        get_position='[lon,lat]',
        get_color='[66, 245, 123]',
        get_radius=50,
        pickable=True,)
    ]


# image = Image.open('/Users/andresgarcia/data/gf_potomacise.jpg')
# box = (100, 100, 400, 400)
# region = image.crop(box)
# st.image(region, caption='Great Falls of the Potomac')

st.title('Potomac Playspot Map')
st.markdown(f'Water level at [Little Falls](https://water.weather.gov/ahps2/hydrograph.php?gage=brkm2&wfo=lwx): {level} ft.')

st.sidebar.title('Potomac Playspot Map')
if st.sidebar.button('All'):
    layers = layers
if st.sidebar.button('Recommended'):
    layers = layers[2:]
if st.sidebar.button('High'):
    layers = layers[:1]
if st.sidebar.button('Low'):
    layers = layers[1:2]

st.pydeck_chart(pdk.Deck(
    #map_style='mapbox://styles/angarcia/ck18kp1td0iwr1cphsbyh6lvr',
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=38.987,
        longitude=-77.241,
        zoom=13
    ),
    layers = layers,
    tooltip={"html": "<b>{name}</b> -- Min: {min}ft, Max: {max}ft",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }}
))