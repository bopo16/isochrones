import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import os
from dotenv import load_dotenv
from osmnx import settings

# load environment variables from .env file
load_dotenv()

# get the API key from the environment variable
api_key = os.getenv("TRAVELTIME_API_KEY")
application_id = os.getenv("TRAVELTIME_APPLICATION_ID")


# set data save location
settings.data_folder = "data"

# filepaths
network_path = os.path.join(settings.data_folder, "network.graphml")
boundary_path = os.path.join(settings.data_folder, "boundary.gpkg")

if not os.path.exists(network_path) or not os.path.exists(boundary_path):
    print("Downloading network and boundary data...")

    # get place boundaries and road network
    place = "Sydney, NSW, Australia"
    gdf = ox.geocode_to_gdf(place)

    G = ox.graph_from_place(place, network_type="walk", retain_all=True)

    # save to disk
    ox.save_graphml(G, filepath=network_path)
    gdf.to_file(boundary_path, driver="GPKG")
else:
    print("Loading data from disk...")
    G = ox.load_graphml(network_path)
    gdf = gpd.read_file(boundary_path)

# plot the network, but do not show it or close it yet
fig, ax = ox.plot_graph(
    G,
    show=False,
    close=False,
    bgcolor="#333333",
    edge_color="w",
    edge_linewidth=0.3,
    node_size=0,
)

# to this matplotlib axis, add the place shape(s)
gdf.plot(ax=ax, fc="k", ec="#666666", lw=1, alpha=1, zorder=-1)

# optionally set up the axes extents
# margin = 0.02
# west, south, east, north = gdf.unary_union.bounds
# margin_ns = (north - south) * margin
# margin_ew = (east - west) * margin
# ax.set_ylim((south - margin_ns, north + margin_ns))
# ax.set_xlim((west - margin_ew, east + margin_ew))
plt.show()
