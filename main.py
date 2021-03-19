import pandas as pd 
import numpy as np
import pydeck as pdk
import requests
import json
import streamlit as st


def get_lvl():
    re = requests.get("https://waterservices.usgs.gov/nwis/iv/?site=01646500&period=PT2H&format=json&variable=00065").text
    jsonData = json.loads(re)
    values = len(jsonData['value']['timeSeries'][0]['values'][0]['value']) - 1
    lvl = jsonData['value']['timeSeries'][0]['values'][0]['value'][values]['value']
    return lvl

    
st.title('Potomac Playspot Map')

level = get_lvl()
st.write(f'Water level at Little Falls: {level} ft')

data = {'lat': [38.99688, 38.97771, 38.97771, 38.97809, 38.97848, 
                38.99489, 38.97965, 38.996983, 38.978755, 38.996391, 38.996226, 
                38.996100, 38.975291, 38.992183, 38.979475, 38.994412, 38.977973, 
                38.990300], 
        'lon': [-77.25243, -77.2359, -77.23589, -77.23646, -77.23433, -77.24867, -77.23566,
                -77.252523, -77.235530, -77.252891, -77.252862, -77.253001, -77.221383,
                -77.248250, -77.232174, -77.249742, -77.237038, -77.247688],
        'min': [2.6,5.2,5.1,4.1,6.8,6.1,7.3,2.6,2.7,3.6,3.3,2.7,4.9,3.9,6.0,
                3.5,2.7,2.5],
        'max': [3.3,5.4,7.0,4.8,8,6.6,8.8,2.8,4.0,3.8,3.6,3.0,5.4,4.8,7.6,
                3.9,4.2,4.3]
        }

df = pd.DataFrame(data)

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
        get_radius=50),

        # below
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'red'],
        get_position='[lon,lat]',
        get_color='[245, 66, 66]',
        get_radius=50),

        # just right
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'green'],
        get_position='[lon,lat]',
        get_color='[66, 245, 123]',
        get_radius=50)
    ]

left_col, left_middle_col, righ_middle_col, right_col = st.beta_columns(4)

if left_col.button('All'):
    layers = layers

if left_middle_col.button('Recommended'):
    layers = layers[2:]

if righ_middle_col.button('High'):
    layers = layers[:1]

if right_col.button('Low'):
    layers = layers[1:2]


st.pydeck_chart(pdk.Deck(
    #map_style='mapbox://styles/angarcia/ck18kp1td0iwr1cphsbyh6lvr',
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=38.987,
        longitude=-77.241,
        zoom=13
    ),
    layers = layers
))