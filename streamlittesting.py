import streamlit as st
import datetime
from mapbox import Geocoder, Directions
import plotly.express as px
import pandas as pd
import requests
from streamlit.components.v1 import html
from streamlit_javascript import st_javascript
import plotly.graph_objects as go
import pygeohash as pgh
import time
from PIL import Image
from io import BytesIO
import folium
from streamlit_folium import st_folium, folium_static


#mapbox setup
access_token = 'pk.eyJ1IjoibXNjb3V0MyIsImEiOiJjbWZnYnNwbmwwY3drMmxwdjQ5N2oybWh6In0.jnEaFseuOaG5C7fchhy6LQ'
geocoder = Geocoder(access_token=access_token)
service = Directions(access_token=access_token)
px.set_mapbox_access_token(access_token)

img_url = "https://s1.ticketm.net/dam/a/7f0/da5c0609-34b5-4c5a-af11-8b609bc927f0_TABLET_LANDSCAPE_LARGE_16_9.jpg"

# img_test = requests.get(img_url)
# img = Image.open(BytesIO(img_test.content))

# st.image(img, width=400)


# x = st.markdown("![](https://s1.ticketm.net/dam/a/7f0/da5c0609-34b5-4c5a-af11-8b609bc927f0_TABLET_LANDSCAPE_LARGE_16_9.jpg)")
# st.image(x, width=400)
#tickemaster setup
tm_api = 'rHRigHQFznnKTxwjJ7lQA1DuzfhqKo6j'

##### create seperate functions?
#---------------------------------------------------------------------------------------------------------------#
##### Function to display map with legs along the route - will need to expand to include other visuals #########
def display_map(location_data):
    fig = go.Figure(go.Scattermap(lat=location_data['latitude'], lon=location_data['longitude'], mode='markers', 
                               marker=go.scattermap.Marker(size=14)))
    
    fig.update_traces(cluster=dict(enabled=True))

    
    # fig = px.line_map(location_data, lat=location_data['latitude'], lon=location_data['longitude'], zoom=13)

    fig.update_layout(map_style='streets', width=1000, height=700)

    return fig
# #---------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------------------------------------------#
########## FOLIUM TEST CODE HERE ###################












#--------------------------------------------------------------------------------------------------------------------#








#---------------------------------------------------------------------------------------------------------------#
### DATA ENTRY FORM
with st.form("vibe_form"):
    st.write("Plan Your Musical Adventure")
    start_date = st.date_input('Start Date',datetime.date.today(),format="MM/DD/YYYY")
    end_date = st.date_input('End Date',datetime.date.today(),format="MM/DD/YYYY")

    start_loc = st.text_input('Start Location')
    destination = st.text_input('Destination')

    how_far = st.slider("Out of the way?", value = 100)

    submitted = st.form_submit_button("Get Vibing!")
#---------------------------------------------------------------------------------------------------------------#


if submitted:
    response_forward_start = geocoder.forward(start_loc)
    response_forward_end = geocoder.forward(destination)


    if response_forward_start.status_code == 200:
        features = response_forward_start.geojson()['features']
        if features:
            first_result = features[0]
            start_coordinates = first_result['geometry']['coordinates']
    if response_forward_end.status_code == 200:
        features = response_forward_end.geojson()['features']
        if features:
            first_result = features[0]
            end_coordinates = first_result['geometry']['coordinates']
    origin = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': start_coordinates}}
    dest = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': end_coordinates}}

    # print(origin)


    directions_response = service.directions([origin, dest], profile='mapbox/driving', steps=True)

    trip_coords = []

    if directions_response.status_code == 200:
        directions_data = directions_response.json()

        route = directions_data['routes'][0] 

        steps = route["legs"][0]["steps"]
        print(len(steps))
        for step in steps:
            trip_coords.append(step["maneuver"]["location"])

    trip_df = pd.DataFrame(trip_coords, columns=['longitude', 'latitude'])

    px_map = display_map(trip_df)

    st.plotly_chart(px_map)

 

    


#---------------------------------------------------------------------------------------------------------------#    
    startDateTime = start_date.strftime("%Y-%m-%d")
    endDateTime = end_date.strftime("%Y-%m-%d")

    geohashes = []
    for _ in range(len(trip_coords)):
        geohashes.append(pgh.encode(trip_coords[_][1], trip_coords[_][0], precision=9))

    # st.write(geohashes)

    showset = set()

    for geohash in geohashes:
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={tm_api}&startDateTime={startDateTime}T00:00:00Z&endDateTime={endDateTime}T23:59:59Z&geoPoint={geohash}&radius={how_far}&unit=miles&size=100'
        response = requests.get(url)
        data = response.json()
        try:
            venue_locations = data["_embedded"]["events"]
            for ven in range(len(venue_locations)):
                showset.add(tuple(venue_locations[ven]["_embedded"]["venues"][0]["location"].values()))
        except: pass
        time.sleep(.5)
    
    showset = list(showset)

    show_locations = pd.DataFrame(showset, columns=['longitude', 'latitude'])

    show_map = display_map(show_locations)

     
    st.plotly_chart(show_map)



#-----------------------------------------------------------------------------------------------------######
    data_rows = []
    col_names = ['attraction', "event_page", "splashart", 
             "tm_segment", "genre", "subgenre", "venue",
             "city", "state", "street", "date", "time", "fam_friendly",
             "longitude", "latitude"
             ]

    for geohash in geohashes:
        url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={tm_api}&startDateTime={startDateTime}T00:00:00Z&endDateTime={endDateTime}T23:59:59Z&geoPoint={geohash}&radius={how_far}&unit=miles&size=100'
        response = requests.get(url)
        data = response.json()
        # st.write(len(data))
        if "_embedded" in data.keys():
            for i in range(len(data["_embedded"]["events"])):

                row_data = []
                try:
                    row_data.append(data["_embedded"]["events"][i]["name"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["url"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["images"][0]["url"])
                except:
                    row_data.append(None)
                try:        
                    row_data.append(data["_embedded"]["events"][i]["classifications"][0]["segment"]["name"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["classifications"][0]["genre"]["name"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["classifications"][0]["subGenre"]["name"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["name"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["city"]["name"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["state"]["stateCode"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["address"]["line1"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["dates"]["start"]["localDate"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["dates"]["start"]["localTime"])
                except:
                    row_data.append(None)
                try:
                    row_data.append(data["_embedded"]["events"][i]["classifications"][0]["family"])
                except:
                    row_data.append(None)
                try:
                    coords = tuple(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["location"].values())
                    long = coords[0]
                    row_data.append(long)
                    
                    # row_data.append(tuple(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["location"].values()[0]))
                except:
                    row_data.append(None)
                try:
                    coords = tuple(data["_embedded"]["events"][i]["_embedded"]["venues"][0]["location"].values())
                    lat = coords[1]
                    row_data.append(lat)
                except:
                    row_data.append(None)   
                data_rows.append(row_data)
        time.sleep(.5)

        
    tm_df = pd.DataFrame(data_rows, columns=col_names)

    tm_df = tm_df.dropna(subset=["event_page"])

    st.dataframe(tm_df)



