import pandas as pd 
import numpy as np
import requests
import json
import streamlit as st
import pydeck as pdk
from PIL import Image

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")

def get_weather():
    url = "http://api.openweathermap.org/data/2.5/weather?lat=38.9741&lon=-77.16329&appid=d17a615c545ef1981aed6b1cb4ada570&units=imperial"
    response = requests.get(url).text
    jsonData = json.loads(response)
    weather = [jsonData['name'], jsonData['weather'][0]['description'], jsonData['main']['temp'],
                jsonData['main']['feels_like'], jsonData['wind']['speed'], jsonData['main']['humidity']]
    return weather

def get_lvl():
    re = requests.get("https://waterservices.usgs.gov/nwis/iv/?site=01646500&period=PT2H&format=json&variable=00065").text
    jsonData = json.loads(re)
    values = len(jsonData['value']['timeSeries'][0]['values'][0]['value']) - 1
    lvl = jsonData['value']['timeSeries'][0]['values'][0]['value'][values]['value']
    return lvl

weather = get_weather()
level = get_lvl()
df = pd.read_csv('https://raw.githubusercontent.com/andGarc/potomackayak/dev/data/locations.csv')

@st.cache(suppress_st_warning=True)
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
        get_radius=10,
        pickable=True,
        radius_scale=2,
        radius_min_pixels=10,
        radius_max_pixels=50),

        # below
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'red'],
        get_position='[lon,lat]',
        get_color='[245, 66, 66]',
        get_radius=10,
        pickable=True,
        radius_scale=2,
        radius_min_pixels=10,
        radius_max_pixels=50),

        # just right
        pdk.Layer('ScatterplotLayer',
        data=df[df['color'] == 'green'],
        get_position='[lon,lat]',
        get_color='[66, 245, 123]',
        get_radius=10,
        pickable=True,
        radius_scale=2,
        radius_min_pixels=10,
        radius_max_pixels=50)
    ]

st.title('Potomac Playspot Map')
st.markdown(f'Water level at [Little Falls](https://water.weather.gov/ahps2/hydrograph.php?gage=brkm2&wfo=lwx): {level} ft')

# Space out the buttons
b1, b2, b3, b4 = st.beta_columns((1, 1, 1, 1))

if b1.button('All'):
    layers = layers
if b2.button('Recommended'):
    layers = layers[2:]
if b3.button('High'):
    layers = layers[:1]
if b4.button('Low'):
    layers = layers[1:2]

b3_df = df[df.color == 'green'].name.to_list()
b3_ls = "\n".join(b3_df)

b4_df = df[(df.color == 'red') | (df.color == 'blue')].name.to_list()
b4_ls = "\n".join(b4_df)


st.pydeck_chart(pdk.Deck(
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

# below map
c1, c2, c3= st.beta_columns((1, 1, 1))

c1.write("Weather :cyclone:")
c1.text(f"{weather[0]}, MD, USA | {weather[1]}")
c1.text(f"{weather[2]} F | Feels like: {weather[3]} F")
c1.text(f"Wind: {weather[4]} mph | Humidity: {weather[5]}%")



c2.write(":sunglasses:")
try:
    c2.text(b3_ls)
except:
    pass

c3.write(":expressionless:")
try:
    c3.text(b4_ls)
except:
    pass
