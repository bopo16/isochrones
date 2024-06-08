import os
import asyncio
import osmnx as ox
import networkx as nx
import geopandas as gpd
from datetime import datetime
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

from download_data_small import data_dir, network_path, boundary_path

# load environment variables from .env file
load_dotenv()

api_key = os.getenv("API_KEY")
app_id = os.getenv("APP_ID")

# define date and time
date_time = "2024-06-07T09:30:00-10:00"

# set destination location
destination = "Central Station, Sydney, Australia"

# get coords for station
geolocator = Nominatim(user_agent="SydneyIsochrones")
location = geolocator.geocode(destination)


# traveltime sdk request
async def main():
    sdk = TravelTimeSdk(app_id, api_key)

    # create list of isochrones
    isochrones = []

    # iterate over request, modifying the travel time
    for traveltime in [10, 20, 30, 45, 60, 90, 120]:
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


# run the traveltime async function and return list of isochrones
isochrones = asyncio.run(main())

# load data
network = ox.load_graphml(network_path)
boundary = gpd.read_file(boundary_path)

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
boundary.plot(ax=ax, fc="lightgrey", ec="white", lw=1, alpha=1, zorder=-1)

# get the colormap for the isochrones
colors = matplotlib.colormaps["RdYlGn_r"]

for i, isochrone in enumerate(isochrones):
    # get the color as a tuple of RGBA values
    rgba_color = colors(i / len(isochrones))

    # convert the RGBA color to a hexadecimal color code
    hex_color = matplotlib.colors.to_hex(rgba_color)

    # plot the isochrone
    isochrone.plot(
        ax=ax, fc=hex_color, ec=None, lw=1, alpha=1, zorder=(len(isochrones) - i)
    )

# plot station location on the map
plt.scatter(location.longitude, location.latitude, color="red", zorder=100)

# show plot
plt.show()
