import dash_leaflet as dl
from dash_extensions.enrich import DashProxy, html
import dash_leaflet.express as dlx
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback, no_update, dash_table, no_update
import requests
from datetime import date, datetime
from mapbox import Geocoder, Directions
import pygeohash as pgh
import time
from flask_caching import Cache
import re
from dotenv import load_dotenv
import os


#Coordinates for approximate U.S geographical center
center = [39.8283, -98.5795]

load_dotenv()


access_token = os.getenv("mapbox_token")
tm_api = os.getenv("ticketmaster_token")

# geo_test = []

#allows markers to be displayed on map using Geojson from Dash Leaflet
point_to_layer_js = """
function(feature, latlng){
    if (feature.properties.display_icon === false) {
        return null; // Don't render a marker for this feature
    }
    // Default marker for features where display_icon is true or not defined
    return L.marker(latlng);
}
"""


app = DashProxy(__name__, title="VibeTrip")

#####---html layout initializing map, input sections, and loading icon.---###################
app.layout = html.Div([
        dl.Map(
        children=[
            dl.TileLayer(),
            # dl.GeoJSON(id="events_to_see", data=None, cluster=True),
            # dl.Polyline(positions=zipped_coords),
            dl.GeoJSON(id="trip_dir_geo", pointToLayer=point_to_layer_js, data=None,),
            dl.Polyline(id="my-polyline", positions=[]),
            dl.GeoJSON(id="along_the_way", data=None, cluster=True),
        ],
        center=center,
        zoom=4,
        style={"height": "50vh"}),    
        dcc.Input(id='input-1-state', type='text', value='Starting Point'),
        dcc.Input(id='input-2-state', type='text', value='Destination'),
        dcc.DatePickerRange(id='input-3-state', min_date_allowed=date.today(), initial_visible_month=date.today()),
        html.Button(id='submit-button-state', n_clicks=0, children='GET VIBING'),
        html.Div([html.H5("How Far Off the Path?")]),
        dcc.Slider(1,100, 1, value = 25, id='how_far', marks = {25: "25", 50: "50", 75:"75", 100:"100"},
                   tooltip={"placement": "bottom", "style":{"color":"SteelBlue", "fontSize": "20px"}, "always_visible": True,
                            "template": "{value} Miles"}),
        html.Div([
            dcc.Dropdown(id="segment-dd", placeholder="Segment (e.g., Music, Sports)", multi=True),
            dcc.Dropdown(id="genre-dd", placeholder="Genre", multi=True),
            dcc.Dropdown(id="city-dd", placeholder="City", multi=True),
            dcc.Dropdown(id="state-dd", placeholder="State", multi=True),
                  
   

        ], style={"display":"grid","gridTemplateColumns":"repeat(5, 1fr)","gap":"8px","marginTop":"8px"}),
         
        html.Div(id='output-state', style={'display':'none'}),
        html.Div([
            html.H5("Search by Name"),
            dcc.Input(id="attraction_filt", value='', type='text') 
        ]),

        dcc.Loading(html.Div([
            dcc.Store(id='tm_df', storage_type='memory'),
            ]),target_components={"tm_df":"*"}
            ),
        dcc.Store(id='filtered_events', storage_type='memory')
    ])
#############################################################################


#############################################################################
#Initial callbacks to the load button which submits user input and starts chain of API calls
@app.callback(
        Output("loading-1", "children"),
        Input("submit-button-state", "n_clicks")
)
def load_output(n):
    if n:
        time.sleep(1)
        return 
    return no_update

######################## Callbacks taking user input that then feeds into program #############
@app.callback(
              Output('trip_dir_geo', 'data'),
              Output('my-polyline', 'positions'),
              Output('output-state', 'children'),
              Output('tm_df', 'data'),
              Input('submit-button-state', 'n_clicks'),
              State('input-1-state', 'value'),
              State('input-2-state', 'value'),
              State('input-3-state', 'start_date'),
              State('input-3-state', 'end_date'),
              State('how_far', 'value')
              )


def update_output(n_clicks, start_loc, destination, start_date, end_date, how_far):
    ###### Section takes start and end points, get directions using mapbox api #######
    geocoder = Geocoder(access_token=access_token)
    service = Directions(access_token=access_token)
    if n_clicks > 0:
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


        directions_response = service.directions([origin, dest], profile='mapbox/driving', steps=True)

        trip_coords = []

###### coordinates are stored in a list, added to a dataframe, which will be added to the map using leaflet

        if directions_response.status_code == 200:
            directions_data = directions_response.json()

            route = directions_data['routes'][0] 

            steps = route["legs"][0]["steps"]
            print(len(steps))
            for step in steps:
                trip_coords.append(step["maneuver"]["location"])

        trip_df = pd.DataFrame(trip_coords, columns=['longitude', 'latitude'])

        startDateTime = datetime.strptime(start_date, "%Y-%m-%d")
        endDateTime = datetime.strptime(end_date, "%Y-%m-%d")
        startDateTime = startDateTime.strftime("%Y-%m-%d")
        endDateTime = endDateTime.strftime("%Y-%m-%d")

        trip_dir_geo = []

        for index, row in trip_df.iterrows():
            build_dict = {
                "lat": row['latitude'],
                "lon": row['longitude']
            }
            trip_dir_geo.append(build_dict)
        
        trip_dir_geo = dlx.dicts_to_geojson(trip_dir_geo)
        my_polyline = list(zip(trip_df['latitude'], trip_df['longitude']))


###### geohashed are calculated from trip coordinates which will be used against tickemaster api ######
        geohashes = []
        for _ in range(len(trip_coords)):
            geohashes.append(pgh.encode(trip_coords[_][1], trip_coords[_][0], precision=9))

######################################################################################################
    data_rows = []
    col_names = ['attraction', "event_page", "splashart", 
             "tm_segment", "genre", "subgenre", "venue",
             "city", "state", "street", "date", "time", "fam_friendly",
             "longitude", "latitude"
             ]

##### Iteration over geohashes, which will be paired with distance and start/end date to collect relevant ticketing information#######

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
        time.sleep(.3) ### rate limit api call 

    if not data_rows:
        return None, trip_dir_geo, my_polyline, "No events found for this route/date window.", None

        
    tm_df = pd.DataFrame(data_rows, columns=col_names)

#### ensure lat/long are numeric type to be able to plot
    tm_df["longitude"] = pd.to_numeric(tm_df["longitude"], errors="coerce")
    tm_df["latitude"]  = pd.to_numeric(tm_df["latitude"], errors="coerce")
    tm_df = tm_df.drop_duplicates(subset=['attraction', 'date', 'time', 'venue'])

#### if no event page, drop as there won't be information to ping
    tm_df = tm_df.dropna(subset=["event_page"])
        
    return trip_dir_geo, my_polyline, f'''
            The Button has been pressed {n_clicks} times,
            Input 1 is "{start_loc}",
            and Input 2 is "{destination},"
            the date range is {start_date} - {end_date}"
            {startDateTime}\n"
            {trip_dir_geo}
        ''', tm_df.to_json(orient='split') ### anything in f string is starter code that won't be seen by user on front end taht was not an easy cleanup


###### callback to add filter options in dropdown menus#######################
@app.callback(
    Output("segment-dd", "options"),
    Output("genre-dd", "options"),
    Output("city-dd", "options"),
    Output("state-dd", "options"),
    Input("tm_df", "data"),
)

def populate_filter_options(rows):

    df = pd.read_json(rows, orient='split')

    def opts(series):
        vals = sorted(v for v in series.dropna().unique() if v not in ("", None))
        return [{"label": v, "value": v} for v in vals]

    return (
        opts(df["tm_segment"]),
        opts(df["genre"]),
        opts(df["city"]),
        opts(df["state"])
    )


########################################################################################

#################### call back which allows users to filter on the filter options loaded after the API call #########
@app.callback(
    Output("filtered_events", "data"),
    Input("tm_df", "data"),
    Input("segment-dd", "value"),
    Input("genre-dd", "value"),
    Input("city-dd", "value"),
    Input("state-dd", "value"),
    Input("attraction_filt", "value"),
    prevent_initial_call = True
)

def apply_filters(rows, seg_vals, genre_vals, city_vals, state_vals, attract):

    dff = pd.read_json(rows, orient='split')

    def multi_filter(dff, col, vals):
        if not vals:
            return dff 
        return dff[dff[col].isin(vals)]
    live_text = attract
    dff = dff[dff['attraction'].str.contains(live_text, case=False, na=False, regex=True)]
    dff = multi_filter(dff, "tm_segment", seg_vals)
    dff = multi_filter(dff, "genre", genre_vals)
    dff = multi_filter(dff, "city", city_vals)
    dff = multi_filter(dff, "state", state_vals)
    return dff.to_json(orient='split')

############################################################################################


############### This section takes the user input from filetering and applies it against the
############## the dataframe holding the event data. 

@app.callback(
    Output("along_the_way", "data"),
    Input("tm_df", "data"),
    Input("filtered_events", "data"),
    prevent_initial_call = True
)

def please_work(rows, filtered):
    
    data = pd.read_json(rows, orient='split')
    filtered = pd.read_json(filtered, orient='split')

    if len(data) == len(filtered):

        geo = []


### this builds the information that will be used for the popup information for events without filters applied
        for index, row in data.iterrows():
            build_dict = {
            "lat": row['latitude'],
            "lon": row['longitude'],
            "popup": f"<b>{row['attraction']} - {row['date'].strftime('%m-%d-%Y')}  {row['time']}</b><br><img src={row['splashart']} alt ='Show Info' width='106'><br><a href={row['event_page']} target='_blank'> Find Tickets </a><br>Venue: {row['venue']}"
        }
            geo.append(build_dict)

        geo = dlx.dicts_to_geojson(geo)

        return geo
### this builds the information that will be used for the popup information for events with filters applied
    else:
        geo = []
        for index, row in filtered.iterrows():
            build_dict = {
            "lat": row['latitude'],
            "lon": row['longitude'],
            "popup": f"<b>{row['attraction']} -  {row['date'].strftime('%m-%d-%Y')} {row['time']}</b><br><img src={row['splashart']} alt ='Show Info' width='106'><br><a href={row['event_page']} target='_blank'> Find Tickets </a><br>Venue: {row['venue']}"
        }
            geo.append(build_dict)

### returns filtered/unfiltered event dataframe to be used in the visualization.
        geo = dlx.dicts_to_geojson(geo)

        return geo
    











if __name__ == "__main__":
    app.run()
