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

# check if the data is already downloaded
if not os.path.exists("data/city.shp") or not os.path.exists("data/graph.graphml"):
    # get the polygon for Parramatta, NSW
    city = ox.geocode_to_gdf("Sydney, NSW, Australia")
    polygon = city["geometry"].iloc[0]

    # get the street network within the polygon
    G = ox.graph_from_polygon(polygon, network_type="walk")

    # save the GeoDataFrame to a shapefile
    city.to_file("data/city.shp")

    # save the Graph to a GraphML file
    ox.save_graphml(G, filepath="data/graph.graphml")
else:
    # load the data from the files
    city = gpd.read_file("data/city.shp")
    G = ox.load_graphml("data/graph.graphml")

# display the objects
fig, ax = ox.plot_graph(G, bgcolor="white", show=False, close=False)
city.plot(ax=ax, facecolor="none", edgecolor="lightgrey")
plt.show()
