# import libraries
import os
import asyncio
import osmnx as ox
import networkx as nx
import geopandas as gpd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib
from geopy.geocoders import Nominatim
from traveltimepy import (
    TravelTimeSdk,
    Coordinates,
    Range,
    PublicTransport,
    Transportation,
)

# ----------------------------------------------------------------------------
# testing flags
full_analysis = False
generate_isochrones = True
download_data = False
full_times = False

# ----------------------------------------------------------------------------
# main

# load environment variables from .env file
load_dotenv()

api_key = os.getenv("API_KEY")
app_id = os.getenv("APP_ID")


# pull data, based on testing flags
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


date_time = check_datetime("2024-06-07T09:30:00-10:00")

# define the range of travel times
if full_times:
    times = [10, 20, 30, 45, 60, 90, 120]
else:
    times = [10, 20, 30]

# get coords for station
geolocator = Nominatim(user_agent="SydneyIsochrones")
location = geolocator.geocode(destination)


# traveltime sdk request
# define the coroutine
async def main():
    sdk = TravelTimeSdk(app_id, api_key)

    # create list of isochrones
    isochrones = []

    # iterate over request, modifying the travel time
    for traveltime in times:
        results = await sdk.time_map_geojson_async(
            coordinates=[Coordinates(lat=location.latitude, lng=location.longitude)],
            arrival_time=date_time,
            travel_time=(traveltime * 60),
            transportation=PublicTransport(walking_time=(traveltime * 60)),
            search_range=Range(enabled=True, width=(30 * 60)),
        )

        # add result (geojson) data to geodataframe
        isochrone = gpd.GeoDataFrame.from_features(results)

        # add gdf to list
        isochrones.append(isochrone)

    return isochrones


if generate_isochrones:
    # run the traveltime async function and return list of isochrones
    isochrones = asyncio.run(main())

    # Check if the directory exists and create it if it doesn't
    if not os.path.isdir(f"{data_dir}/isochrones"):
        os.makedirs(f"{data_dir}/isochrones")

    # save isochrones to disk
    for i, isochrone in enumerate(isochrones):
        isochrone_path = os.path.join(data_dir, f"isochrones/isochrone_{i}.gpkg")
        try:
            isochrone.to_file(isochrone_path, driver="GPKG")
        except Exception as e:
            print(f"Error writing isochrone {i}: {e}")
else:
    # load locally saved isochrones
    isochrones = []
    for i in range(len(times)):
        isochrones.append(gpd.read_file(f"{data_dir}/isochrones/isochrone_{i}.gpkg"))


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
boundary.plot(
    ax=ax, fc="lightgrey", ec="white", lw=1, alpha=1, zorder=(len(isochrones) * -1 - i)
)

# get the colormap for the isochrones
colors = matplotlib.colormaps["RdYlGn_r"]

for i, isochrone in enumerate(isochrones):
    # get the color as a tuple of RGBA values
    rgba_color = colors(i / len(isochrones))

    # convert the RGBA color to a hexadecimal color code
    hex_color = matplotlib.colors.to_hex(rgba_color)

    # plot the isochrone
    isochrone.plot(
        ax=ax, fc=hex_color, ec=None, lw=1, alpha=1, zorder=(len(isochrones) * -1 - i)
    )

# plot station location on the map
plt.scatter(location.longitude, location.latitude, color="red", zorder=100)

# show plot
plt.show()
