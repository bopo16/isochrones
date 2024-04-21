import os
import osmnx as ox

data_dir = "data"

# Check if the data directory exists, create it if it doesn't
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Define the place name and network types
place = "Sydney, NSW, Australia"

# Download data
network = ox.graph_from_place(place, network_type="walk", retain_all=True)
boundary = ox.geocode_to_gdf(place)

# Define the filepaths
network_path = os.path.join(data_dir, "network.graphml")
boundary_path = os.path.join(data_dir, "boundary.gpkg")

# Save data
ox.save_graphml(network, filepath=network_path)
boundary.to_file(boundary_path, driver="GPKG")
