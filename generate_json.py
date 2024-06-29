import json
import copy

def build_json_query(location, date_time, times):

    # Base structure for an arrival_search item
    base_arrival_search = {
        "id": "isochrone-0",
        "coords": {
            "lat": location.latitude,
            "lng": location.longitude,
        },
        "arrival_time": date_time,
        "travel_time": None,  # This will be set dynamically
        "transportation": {
            "type": "public_transport",
            "walking_time": None,
            "parking_time": 0,
            "boarding_time": 15,
            "pt_change_delay": 15,
            "disable_border_crossing": False,
        },
        "level_of_detail": {"scale_type": "simple", "level": "medium"},
        "no_holes": False,
        "range": {"enabled": True, "width": None},
    }

    # Initialize the data dictionary with an empty list for arrival_searches
    data = {"arrival_searches": []}

    # Loop through each traveltime and create an arrival_search item
    for traveltime in times:
        # Create a copy of the base arrival_search to modify
        arrival_search = copy.deepcopy(base_arrival_search)
        arrival_search["id"] = f"isochrone-{traveltime}"
        arrival_search["travel_time"] = traveltime*60
        arrival_search["transportation"]["walking_time"] = traveltime*60
        arrival_search["range"]["width"] = 30*60

        # Append the modified arrival_search to the list
        data["arrival_searches"].append(arrival_search)

    # Convert data dictionary to JSON string
    json_data = json.dumps(data, indent=2)

    return json_data

# ----------------------------------------------------------------------------
# testing

# from geopy.geocoders import Nominatim
# from dotenv import load_dotenv
# import os

# # load environment variables from .env file
# load_dotenv()

# api_key = os.getenv("API_KEY")
# app_id = os.getenv("APP_ID")


# times = [10, 20, 30]
# arrival_time = "2024-06-29T09:30:00-10:00"

# # set destination location
# destination = "Central Station, Sydney, Australia"
# # get coords for station
# geolocator = Nominatim(user_agent="SydneyIsochrones")
# location = geolocator.geocode(destination)

# print(location)
# print(f"lat = {location.latitude}")
# print(f"lng = {location.longitude}")


# json_data = build_json_query(location, arrival_time, times)
# print(json_data)


# import requests

# url = "https://api.traveltimeapp.com/v4/time-map"
# headers = {
#     "Content-Type": "application/json",
#     "Accept": "application/geo+json",
#     "X-Application-Id": app_id,
#     "X-Api-Key": api_key,
# }


# r = requests.post(url, headers=headers, data=json_data)

# # Check the r (optional)
# if r.status_code == 200:
#     print("Success!")
#     isochrones = r.json()
# else:
#     print("Failed.", r.status_code)
