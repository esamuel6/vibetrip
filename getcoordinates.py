from mapbox import Geocoder, Directions
import json
import base64
import requests
import pygeohash as pgh
import time


tm_api = 'rHRigHQFznnKTxwjJ7lQA1DuzfhqKo6j'
access_token = 'pk.eyJ1IjoibXNjb3V0MyIsImEiOiJjbWZnYnNwbmwwY3drMmxwdjQ5N2oybWh6In0.jnEaFseuOaG5C7fchhy6LQ'

geocoder = Geocoder(access_token=access_token)
service = Directions(access_token=access_token)

start_address = 'Philladelphia, PA'
end_address = 'Baltimore, MA'

response_forward_start = geocoder.forward(start_address)
response_forward_end = geocoder.forward(end_address)

#use geocode forwarding to get coordinates for directions api 
#create function in final code base
if response_forward_start.status_code == 200:
    features = response_forward_start.geojson()['features']
    if features:
        first_result = features[0]
        start_coordinates = first_result['geometry']['coordinates']
        place_name = first_result['place_name']
        # print(f"Forward Geocoding Result for '{start_address}':")
        # print(f"  Coordinates (Lon, Lat): {start_coordinates}")
        # print(f"  Place Name: {place_name}")
    else:
        print(f"No results found for '{start_address}'")
else:
    print(f"Error during forward geocoding: {response_forward_start.status_code}")

if response_forward_end.status_code == 200:
    features = response_forward_end.geojson()['features']
    if features:
        first_result = features[0]
        end_coordinates = first_result['geometry']['coordinates']
        place_name = first_result['place_name']
        # print(f"Forward Geocoding Result for '{end_address}':")
        # print(f"  Coordinates (Lon, Lat): {end_coordinates}")
        # print(f"  Place Name: {place_name}")
    else:
        print(f"No results found for '{end_address}'")
else:
    print(f"Error during forward geocoding: {response_forward_end.status_code}")


origin = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': start_coordinates}}
destination = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': end_coordinates}}

# print(origin)
#try post method for mapbox api



directions_response = service.directions([origin, destination], profile='mapbox/driving', steps=True)

trip_coordinates = []

if directions_response.status_code == 200:
    directions_data = directions_response.json()

    route = directions_data['routes'][0] 

    steps = route["legs"][0]["steps"]
    # print(len(steps))
    for step in steps:
        trip_coordinates.append(step["maneuver"]["location"])


else:
    print(f'Error fetching direcitons: {directions_response.status_code}')

# print(trip_coordinates)    

geohash = pgh.encode(trip_coordinates[0][1], trip_coordinates[0][0], precision=9)
# geohash = pgh.encode(38.253246, -85.758804, precision=9)
# print(geohash)





url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={tm_api}&startDateTime=2025-10-30T00:00:00Z&endDateTime=2025-11-07T23:59:59Z&geoPoint={geohash}&radius=50&unit=miles&size=100'

# # url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={tm_api}&startDateTime=2025-10-25T00:00:00Z&endDateTime=2025-10-31T23:59:59Z&postalCode=40202&radius=50&unit=miles'

# # # url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={tm_api}&city=Louisville&stateCode=KY&localStartDateTime=2025-10-25T00:00:00,2025-10-25T23:59:59&sort=date,asc'

response = requests.get(url)
data = response.json()
# print(data)

# print(data.keys())

# print(len(data))

# for event in data["_embedded"]["events"]:
#     print(event["name"])
# 
# ------------ returns key details of events -----------------#########  
# [4] is a placeholder value that can be iterated over    
print(f"Attraction: {data["_embedded"]["events"][4]["name"]}") #attraction name
print(f"Event page: {data["_embedded"]["events"][4]["url"]}") #url to event page
print(f"splashart: {data["_embedded"]["events"][4]["images"][0]["url"]}") #link to splashart? I hope
print(f"tm segment: {data["_embedded"]["events"][4]["classifications"][0]["segment"]["name"]}") #TM Segment as shown on site????
print(f"Genre {data["_embedded"]["events"][4]["classifications"][0]["genre"]["name"]}") #genre
print(f"subgengre: {data["_embedded"]["events"][4]["classifications"][0]["subGenre"]["name"]}") #subgenre
print(f"Venue: {data["_embedded"]["events"][4]["_embedded"]["venues"][0]["name"]}") #venue name)
print(f"City: {data["_embedded"]["events"][4]["_embedded"]["venues"][0]["city"]["name"]}") #city of venue
print(f"State: {data["_embedded"]["events"][4]["_embedded"]["venues"][0]["state"]["stateCode"]}") #state of venue
print(f"Street Address {data["_embedded"]["events"][4]["_embedded"]["venues"][0]["address"]["line1"]}") #address of venue
print(f"date: {data["_embedded"]["events"][4]["dates"]["start"]["localDate"]}") #day of event start
print(f"Time: {data["_embedded"]["events"][4]["dates"]["start"]["localTime"]}") #time of event start
print(f"Fam Friendly: {data["_embedded"]["events"][4]["classifications"][0]["family"]}") #family friendly ?? 

###-----------------------------------------------------------------########################

##----- Check if events have price available ----######
# for event in range(len(data["_embedded"]["events"])):
#     try:
#         print(f"{event} cost {data["_embedded"]["events"][event]["priceRanges"]}")
#     except:
#         print(f"haha {event} is free")


# for key in data["_embedded"]["events"][4]["_embedded"]:
#     print(key, data["_embedded"]["events"][4]["_embedded"][key], '\n')

#pulls location of venue in long/lat format - might need to look at putting this as a tuple
# print(data["_embedded"]["events"][0]["_embedded"]["venues"][0]["location"].values())
# x = list(data["_embedded"]["events"][0]["_embedded"]["venues"][0]["location"].values())


# print(x)
# print(data["_embedded"]["events"][0].keys())

# geohashes = []
# for _ in range(len(trip_coordinates)):
#     geohashes.append(pgh.encode(trip_coordinates[_][1], trip_coordinates[_][0], precision=9))


# showset = set()

# for geohash in geohashes:
#     url = f'https://app.ticketmaster.com/discovery/v2/events.json?apikey={tm_api}&startDateTime=2025-10-29T00:00:00Z&endDateTime=2025-11-10T23:59:59Z&geoPoint={geohash}&radius=50&unit=miles'
#     response = requests.get(url)
#     data = response.json()
#     venue_locations = data["_embedded"]["events"]
#     for ven in range(len(venue_locations)):
#         x = tuple(venue_locations[ven]["_embedded"]["venues"][0]["location"].values())
#         showset.add(x)
#         # showset.add(venue_locations[ven]["_embedded"]["venues"][0]["location"].values())
#     time.sleep(.5)


# print(showset)
