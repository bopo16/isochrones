# import libraries
import os
import sys
import json
import requests
import numpy as np
import osmnx as ox
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from matplotlib.colors import to_hex
from geopy.geocoders import Nominatim
from generate_json import build_json_query
from datetime import datetime, timedelta, timezone
from shapely.geometry import Polygon, MultiPolygon

# ----------------------------------------------------------------------------
# testing flags
full_analysis = True
generate_isochrones = True
download_data = False
full_times = True

# ----------------------------------------------------------------------------
# main

# load environment variables from .env file
load_dotenv()

api_key = os.getenv("API_KEY")
app_id = os.getenv("APP_ID")


# set parameters
if full_analysis:
    # Define the place name and network types
    place = "Sydney, NSW, Australia"

    # set destination location
    destination = "Central Station, Sydney, Australia"
else:
    # Define the place name and network types
    place = "Parramatta, NSW, Australia"

    # set destination location
    destination = "Parramatta Station, Sydney, Australia"


# set downloaded data directory
data_dir = "data"

# Check if the data directory exists, create it if it doesn't
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Define the filepaths
network_path = os.path.join(data_dir, "network.graphml")
boundary_path = os.path.join(data_dir, "boundary.gpkg")

# download map data or load from disk
if download_data:
    # download map data
    network = ox.graph_from_place(place, network_type="walk", retain_all=True)
    boundary = ox.geocode_to_gdf(place)

    # Save data
    ox.save_graphml(network, filepath=network_path)
    boundary.to_file(boundary_path, driver="GPKG")
else:
    # load map data from disk
    network = ox.load_graphml(network_path)
    boundary = gpd.read_file(boundary_path)


# define arrival data and time
def check_datetime(date_time):
    # check if selected time is within a two week window
    current_time = datetime.now(timezone.utc)
    date_time_obj = datetime.fromisoformat(date_time).astimezone(timezone.utc)
    two_weeks_ago = current_time - timedelta(weeks=2)
    two_weeks_future = current_time + timedelta(weeks=2)

    # Check if the date_time_obj is within the two-week window
    if date_time_obj < two_weeks_ago or date_time_obj > two_weeks_future:
        # If not, return current datetime
        return current_time.isoformat()
    else:
        # Otherwise, return the original datetime string
        return date_time

date_time = check_datetime("2024-06-29T09:30:00-10:00")


# define the range of travel times
if full_times:
    times = [10, 20, 30, 45, 60, 90, 120]
else:
    times = [10, 20, 30]


# get coords for station
geolocator = Nominatim(user_agent="SydneyIsochrones")
location = geolocator.geocode(destination)


# traveltime API POST request
# generate json body data
json_data = build_json_query(location, date_time, times)

url = "https://api.traveltimeapp.com/v4/time-map"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/geo+json",
    "X-Application-Id": app_id,
    "X-Api-Key": api_key,
}


# send API request for isocrones, or load from disk
if generate_isochrones:
    # send POST request
    r = requests.post(url, headers=headers, data=json_data)

    # Check the response
    if r.status_code == 200:
        print("Success!")

        # Save GeoJSON to disk
        with open(f"{data_dir}/isochrones.geojson", "w") as f:
            json.dump(r.json(), f)

        # add result (geojson) data to geodataframe
        isochrone = gpd.GeoDataFrame.from_features(r.json())

    else:
        # print error message and exit
        print("Failed.", r.status_code)
        print(r.json())
        sys.exit(1)
else:
    # load locally saved isochrones
    with open(f"{data_dir}/isochrones.geojson", "r") as f:
        r = json.load(f)

    # add geojson data to geodataframe
    isochrone = gpd.GeoDataFrame.from_features(r)

# print isochrone gdf for reference
print(isochrone)


# plot the network, but do not show it or close it yet
fig, ax = ox.plot_graph(
    network,
    show=False,
    close=False,
    bgcolor="white",
    edge_color="white",
    edge_linewidth=0.3,
    node_size=0,
)


# to this matplotlib axis, add the place shape(s)
boundary.plot(ax=ax, fc="lightgrey", ec="white", lw=1, alpha=1, zorder=-20)


# map each unique search_id to a color
# list of unique search_ids (isochrone ids)
unique_search_ids = isochrone["search_id"].unique()

# get distinct colours from colourmap
colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(unique_search_ids)))

# map each search_id to a color
search_id_to_color = {
    search_id: color for search_id, color in zip(unique_search_ids, colors)
}

# plot each polygon with its corresponding color
# loop through the gdf and extract each polygon/multipolygon
for idx, row in isochrone.iterrows():
    geom = row.geometry
    search_id = row.search_id
    color = search_id_to_color[search_id] 

    # check if poly or multipoly and handle geometry accordingly
    if isinstance(geom, Polygon):
        polygons = [geom]
    elif isinstance(geom, MultiPolygon):
        polygons = geom.geoms
    else:
        continue  # Skip non-Polygon/MultiPolygon geometries

    # plot contents of `polygons` and adjust colour and colour and zorder
    for i, poly in enumerate(polygons):
        gdf = gpd.GeoDataFrame(index=[0], crs=isochrone.crs, geometry=[poly])
        gdf.plot(
            ax=ax,
            color=to_hex(color),
            edgecolor=None,
            alpha=0.8,
            zorder=(len(isochrone) - i + 10),
        )


# plot station location on the map
plt.scatter(location.longitude, location.latitude, color="red", zorder=100)

# show plot
plt.show()
