Project Title:
    VibeTrip
Project Description:
    VibeTrip transforms routine road trips into dynamic adventures by recommending live events along a traveler’s route.  
Using Mapbox and Ticketmaster APIs, the application lets users input trip details — start and end points, dates, and event radius — to discover concerts, sports, and cultural events that match their preferences.  

Unlike traditional route planners that only show static locations (e.g., gas stations or restaurants), VibeTrip connects travelers to live experiences on their journey. The backend uses Mapbox and Python to process route coordinates, convert them into geohashes, and query the Ticketmaster API for nearby events.  
These events are visualized on a Dash Leaflet map interface, where users can filter by event type, genre, city, state. Users can also use the text search feature to filter for events by name. 

Goal:
    Enhance the road-trip experience by blending travel planning with real-time event discovery.

---

## Installation

**Requirements:**
- Python 3.13.x  
- Visual Studio Code with Python virtual environment (recommended)  
- Internet connection (for Mapbox & Ticketmaster API access)

**Steps:**
1. Ensure all project files (`vibetrip.py`, `requirements.txt`, etc.) are in the same directory within VSCode project  
2. Open a terminal in that directory.  
3.a Install dependencies:
   ```bash
   py -m pip install -r requirements.txt
3.b Python libraries to install if the requirements.txt file does not work as intended
dash_leaflet
dash_extensions
pandas
dash
datetime
mapbox
pygeohash
flask_caching
python-dotenv
dash
dotenv

Execution

1. Run Python file
2. Open local server http://127.0.0.1:8050
3. Vibetrip should open in the system default browser
4. To use vibetrip, enter the following user input:
Starting Point (within Continental US/Canada)
Destination (within Continental US/Canada)
Anticipated dates of travel
Start Date
End Date
Adjust slider to adjust search radius
5. Click ‘Get Vibing’
Results can take up to a minute to populate.
6. To adjust visualization, use any combination of filters.
7. Individual markers can be clicked to populate event data. 

Video Installation and Execution 
https://www.youtube.com/watch?v=eKXIfIvegT0&feature=youtu.be

Credit: Alexandria La Verde, Elizabeth Samuel, Kristie Garrison, Mark Scout
