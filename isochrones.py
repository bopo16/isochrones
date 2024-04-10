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

# define options
place = "Sydney, NSW, Australia"
tiles = "cartodbdarkmatter"
mk = {"radius": 6}

import os
import osmnx as ox
from osmnx import settings
import geopandas as gpd

# DataHandler class that takes care of downloading, saving, and loading the data.
# The save and load methods check the file extension and use the appropriate function to save or load the data.
# The handle method checks if the file exists.
#   If it does, it loads the data from the file.
#   If it doesn't, it downloads the data and saves it to the file.
class DataHandler:
    def __init__(self, name, download_func):
        self.name = name
        self.download_func = download_func
        self.filepath = os.path.join(settings.data_folder, name)

    def handle(self):
        if not os.path.exists(self.filepath):
            print(f"Downloading {self.name}...")
            data = self.download_func()
            self.save(data)
        else:
            print(f"Loading {self.name} from disk...")
            data = self.load()
        return data

    def save(self, data):
        if self.name.endswith('.gpkg'):
            data.to_file(self.filepath, driver="GPKG")
        elif self.name.endswith('.graphml'):
            ox.save_graphml(data, filepath=self.filepath)

    def load(self):
        if self.name.endswith('.gpkg'):
            return gpd.read_file(self.filepath)
        elif self.name.endswith('.graphml'):
            return ox.load_graphml(self.filepath)

# Define the data handlers
data_handlers = [
    DataHandler(
        "roads.graphml",
        download_func=lambda: ox.graph_from_place(place, network_type="walk", retain_all=True)
    ),
    DataHandler(
        "boundary.gpkg",
        download_func=lambda: ox.geocode_to_gdf(place)
    ),
    DataHandler(
        "rail.gpkg",
        download_func=lambda: ox.features_from_place(place, tags={"railway": "light_rail"})
    )
]

# Handle the data
for handler in data_handlers:
    data = handler.handle()
    if handler.name == "roads.graphml":
        G = data
    elif handler.name == "boundary.gpkg":
        boundary = data
    elif handler.name == "rail.gpkg":
        rail = data
        
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
boundary.plot(ax=ax, fc="k", ec="#666666", lw=1, alpha=1, zorder=-1)

# optionally set up the axes extents
# margin = 0.02
# west, south, east, north = gdf.unary_union.bounds
# margin_ns = (north - south) * margin
# margin_ew = (east - west) * margin
# ax.set_ylim((south - margin_ns, north + margin_ns))
# ax.set_xlim((west - margin_ew, east + margin_ew))
plt.show()
