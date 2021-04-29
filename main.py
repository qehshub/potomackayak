import pandas as pd 
import numpy as np
import requests
import json
import streamlit as st
import pydeck as pdk
import time
import datetime
import plotly.express as px
from PIL import Image
from bs4 import BeautifulSoup

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide")



### *********************************************
# generate level chart
# request data from api
response = requests.get("https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=brkm2&output=tabular&time_zone=edt")

soup = BeautifulSoup(response.text, 'html.parser')
h_elem = soup.find_all('tr')
time = []
level_ft = []
level_kcfs = []

for sec in h_elem:
  for e in sec:
    try:
      if '/' in e.text:
        time.append(e.text)
      elif 'ft' in e.text:
        lvl = e.text[:-2]
        level_ft.append(lvl)
      elif 'kcfs' in e.text:
        lvl = e.text[:-4]
        level_kcfs.append(lvl)
    except:
      pass

df_lvl = pd.DataFrame({'time': time[2:], 'level_ft': level_ft, 'level_kcfs': level_kcfs})

def split_time_date(r):
  tt = r.time.split()
  tt[0] = tt[0] + "/2021"
  tt[1] = tt[1].split(":")
  tmp = tt[1]
  tt[1] = tmp[0]
  tt.append(tmp[1])

  str1 = f"{tt[0]} {tt[1]}:{tt[2]}"
  element = datetime.datetime.strptime(str1,"%m/%d/%Y %H:%M")
  r.timestamp = element

df_lvl["timestamp"] = ""
df_lvl.apply(split_time_date, axis=1)

now = datetime.datetime.now() - datetime.timedelta(hours=4)
df_lvl = df_lvl.sort_values(by=['timestamp'])
df_lvl['obs_pred'] = df_lvl['timestamp'].apply(lambda x: "Observed" if (x < now) else "Predicted")
df_lvl['level_ft'] = df_lvl['level_ft'].astype(float)

fig = px.line(df_lvl, x="timestamp", y="level_ft", color = "obs_pred", hover_name="level_ft",
        line_shape="spline", render_mode="svg")

fig.update_layout(

    autosize = True,
    width=800,
    height=250
)

### *********************************************


def get_weather():
    key = st.secrets["weather_api_key"]
    url = f"http://api.openweathermap.org/data/2.5/weather?lat=38.9741&lon=-77.16329&appid={key}&units=imperial"
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
my_expander = st.beta_expander("Expand me to see map filters...", expanded=True)
with my_expander:
    b1, b2, b3, b4 = st.beta_columns((1, 1, 1, 1))
    b_all = b1.button('All')
    b_rec = b2.button('Recommended')
    b_high = b3.button('High')
    b_low = b4.button('Low')


if b_all:
    layers = layers
if b_rec:
    layers = layers[2:]
if b_high:
    layers = layers[:1]
if b_low:
    layers = layers[1:2]

b3_df = df[df.color == 'green'].name.reset_index(drop=True)
b4_df = df[(df.color == 'red') | (df.color == 'blue')].name.reset_index(drop=True)

bb1, bb2 = st.beta_columns(((2,1)))

bb1.pydeck_chart(pdk.Deck(
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

# next to map
bb2.write("Weather :cyclone:")
bb2.text(f"{weather[0]}, MD, USA | {weather[1]}")
bb2.text(f"{weather[2]} F | Feels like: {weather[3]} F")
bb2.text(f"Wind: {weather[4]} mph | Humidity: {weather[5]}%")

bb2.write("Go here :sunglasses:")
try:
    bb2.dataframe(b3_df)
except:
    pass

bb2.write(":expressionless: maybe avoid...")
try:
    bb2.dataframe(b4_df, height=120)
except:
    pass


# below map
col1, col2, col3 = st.beta_columns([1,6,1])
with col1:
    st.write("")

with col2:
    st.plotly_chart(fig)


