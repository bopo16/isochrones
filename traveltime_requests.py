import os
import requests
from dotenv import load_dotenv

# similar to the traveltimesdk function in `plot_data.py`, but getting the data as a POST
# request instead of using the SDK. This might be useful for combining multiple isochrones 
# into one request. 

# load environment variables from .env file
load_dotenv()

api_key = os.getenv("API_KEY")
app_id = os.getenv("APP_ID")

# define URL
url = "https://api.traveltimeapp.com/v4/time-map"

# define request headers
headers = {
    "Content-Type": "application/json",
    "Accept": "application/geo+json",
    "X-Application-Id": app_id,
    "X-Api-Key": api_key,
}

# define request body
data = {
    "arrival_searches": [
        {
            "id": "isochrone-0",
            "coords": {"lat": -33.8698439, "lng": 151.2082848},
            "arrival_time": "2024-04-21T23:30:00.000Z",
            "travel_time": 1800,
            "transportation": {
                "type": "public_transport",
                "walking_time": 900,
                "cycling_time_to_station": 100,
                "parking_time": 0,
                "boarding_time": 0,
                "driving_time_to_station": 1800,
                "pt_change_delay": 0,
                "disable_border_crossing": false,
            },
            "level_of_detail": {"scale_type": "simple", "level": "medium"},
            "no_holes": false,
            "polygons_filter": {"limit": 100},
            "range": {"enabled": true, "width": 900},
        }
    ]
}
