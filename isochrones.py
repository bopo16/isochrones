
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# get the API key from the environment variable
api_key = os.getenv("TRAVELTIME_API_KEY")
application_id = os.getenv("TRAVELTIME_APPLICATION_ID")

# get the polygon for Parramatta, NSW
city = ox.geocode_to_gdf('Parramatta, NSW, Australia')
polygon = city['geometry'].iloc[0]

# get the street network within the polygon
G = ox.graph_from_polygon(polygon, network_type='walk')

# display the objects
fig, ax = ox.plot_graph(G, bgcolor='white', show=False, close=False)
city.plot(ax=ax, facecolor='none', edgecolor='lightgrey')
plt.show()


