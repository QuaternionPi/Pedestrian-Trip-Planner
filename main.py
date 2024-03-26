from sys import argv
import os
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from collections import namedtuple
from typing import Callable
from util import *
from cache_from_osm import cache_from_osm, cache_osm_exists, read_from_cache
from graph import *

pd.options.display.max_rows = 5000  # Max rows pandas will print in a dataframe

# useful for graphing
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra
# https://medium.com/analytics-vidhya/interative-map-with-osm-directions-and-networkx-582c4f3435bc


def rate_point(x: float, y: float):
    pass


def is_skytrain(row) -> bool:
    name: str = str(row.train_name)
    return "SkyTrain" in name


# Get metro rail routes, in Vancouver that's the SkyTrain
def get_metro_rail() -> gpd.GeoDataFrame:
    railways: gpd.GeoDataFrame = read_from_cache("railways")
    railways["train_name"] = railways["name"]
    mask: gpd.GeoSeries = railways.apply(is_skytrain, axis=1)
    skytrain: gpd.GeoDataFrame = railways[mask]
    return skytrain


def is_parking(row) -> bool:
    name: str = str(row.traffic_name)
    fclass: str = str(row.fclass)
    return "parking" in name.lower() or ("parking" in fclass and "under" not in fclass)


# Get above ground parking lots
def get_parking() -> gpd.GeoDataFrame:
    traffic: gpd.GeoDataFrame = read_from_cache("traffic")

    # "name" is a reserved keyword in pandas, so choose another
    traffic["traffic_name"] = traffic["name"]

    mask: gpd.GeoSeries = traffic.apply(is_parking, axis=1)
    parking: gpd.GeoDataFrame = traffic[mask]
    return parking


def get_landuse_positive() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = read_from_cache("landuse")
    key: str = (
        "nature_reserve|park|retail|forest|recreation_ground|grass|commercial|meadow|orchard|vineyard"
    )
    positive: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return positive


def get_landuse_neutral() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = read_from_cache("landuse")
    key: str = "cemetary|scrub|health"
    neutral: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return neutral


def get_landuse_negative() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = read_from_cache("landuse")
    key: str = "farmland|military|allotments|quarry"
    negative: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return negative


def walkable(roads: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # Define a list of road classes considered walkable
    walkable_classes = ['footway', 'pedestrian', 'path', 'residential', 'living_street']

    # Create a boolean mask that identifies rows where the 'fclass' column matches any of the walkable classes
    walkable_criteria = roads['fclass'].isin(walkable_classes)

    # Use the mask to filter the DataFrame, selecting only the walkable roads
    walkable_roads: gpd.GeoDataFrame = roads[walkable_criteria]

    return walkable_roads


def get_walkable_roads() -> gpd.GeoDataFrame:
    raw_roads: gpd.GeoDataFrame = walkable(read_from_cache("roads"))

    raw_graph: nx.Graph = gdf_to_graph(split_geometry(raw_roads))
    raw_graph.remove_edges_from(nx.selfloop_edges(raw_graph))

    graph = largest_component(raw_graph)
    roads = graph_to_gdf(graph)
    return roads


def simple_niceness(pos: tuple[float, float], landuse: gpd.GeoDataFrame) -> float:

    # TODO: How nice is position, defined by landuse

    pass


def plan_route(
    roads_graph: nx.MultiGraph,
    weight: Callable[[tuple[float, float], gpd.GeoDataFrame], float] = simple_niceness,
) -> nx.MultiGraph:

    # TODO: Plan a single route from a graph

    pass


def to_gpx_studio(path: list[nx.MultiGraph]) -> None:

    # TODO: Map the paths as gpx in GPX Studio

    pass


# Main function and entry point of program execution
if __name__ == "__main__":
    folder: str = argv[1]

    # If there is no cache of location-limited files then create one
    if not cache_osm_exists():
        cache_from_osm(folder)

    roads: gpd.GeoDataFrame = get_walkable_roads()
    graph: nx.MultiGraph = gdf_to_graph(roads)

    # Path between the SFU Dinning Hall to the AQ Pond
    dinning_hall: Location = Location(-122.924745, 49.279980)
    aq_pond: Location = Location(-122.917446, 49.278985)
    path_nodes: list[tuple[float, float]] = shortest_path(graph, dinning_hall, aq_pond)
    path_graph: nx.MultiGraph = graph.subgraph(path_nodes)
    path_gdf: nx.graph = graph_to_gdf(path_graph)

    # Plot path and roads, with roads in the background
    roads_plot: tuple[plt.Figure, plt.Axes] = roads.plot()
    path_polt: tuple[plt.Figure, plt.Axes] = path_gdf.plot(
        ax=roads_plot, color="red"
    )

    # Plot landuse over top of roads and the path
    landuse: gpd.GeoDataFrame = read_from_cache("landuse")
    landuse.plot(ax=path_polt, color="green")
    plt.show()
    input()
