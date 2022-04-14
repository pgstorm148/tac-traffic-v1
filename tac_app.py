import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
#import geopandas as gpd
#import shapefile 


#sf = shapefile.Reader("Vadodara1.shp")

#Shapefile addition try
#shapefile = gpd.read_file("Vadodara1.shp")
#print(shapefile)

# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")

# LOADING DATA
DATE_TIME = "date/time"


@st.experimental_memo
def load_data(nrows):
    data = pd.read_csv("tac111.csv.gz", nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
    return data

data = load_data(100000)

# CREATING FUNCTION FOR MAPS

def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["lon", "lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

# LAYING OUT THE TOP SECTION OF THE APP
row1_1, row1_2 = st.columns((2,3))

with row1_1:
    st.title("Vadodara City Traffic Analysis")
    hour_selected = st.slider("Select hour of pickup", 0, 23)

with row1_2:
    st.write(
    """
    ##
   Traffic data wrt time and help of google maps
    By sliding the slider on the left you can view different slices of time and explore different traffic trends.
    """)

# FILTERING DATA BY HOUR SELECTED
data = data[data[DATE_TIME].dt.hour == hour_selected]

# LAYING OUT THE MIDDLE SECTION OF THE APP WITH THE MAPS
row2_1, row2_2, row2_3, row2_4 = st.columns((2,1,1,1))

# SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
vip_circle= [22.327209, 73.213652]  #laguardia
eva = [22.2724, 73.1876] #jfk
kalaghoda = [22.3089, 73.1880] #newark
zoom_level = 12
midpoint = (np.average(data["lat"]), np.average(data["lon"]))
m11 = [22.3173, 73.1667]

with row2_1:
    st.write("**All Vadodara City from %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))
    #map(data, midpoint[0], midpoint[1], 11)
    map(data, m11[0], m11[1], 11)

with row2_2:
    st.write("**VIP CIrcle(Near Airport)**")
    map(data, vip_circle[0],vip_circle[1], zoom_level)

with row2_3:
    st.write("**Eva mall circle**")
    map(data, eva[0],eva[1], zoom_level)

with row2_4:
    st.write("**kalaghoda circle**")
    map(data, kalaghoda[0],kalaghoda[1], zoom_level)

# FILTERING DATA FOR THE HISTOGRAM
filtered = data[
    (data[DATE_TIME].dt.hour >= hour_selected) & (data[DATE_TIME].dt.hour < (hour_selected + 1))
    ]

hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]

chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

# LAYING OUT THE HISTOGRAM SECTION

st.write("")

st.write("**Breakdown of rides per minute between %i:00 and %i:00**" % (hour_selected, (hour_selected + 1) % 24))

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ).configure_mark(
        opacity=0.2,
        color='red'
    ), use_container_width=True)
