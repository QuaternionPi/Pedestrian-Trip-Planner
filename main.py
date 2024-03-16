from sys import argv
import os
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from collections import namedtuple
from util import *
from cache_from_osm import cache_from_osm, cache_osm_exists, read_from_cache

from graph import *

pd.options.display.max_rows = 5000

# useful for graphing
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra
# https://medium.com/analytics-vidhya/interative-map-with-osm-directions-and-networkx-582c4f3435bc


def rate_point(x: float, y: float):
    pass


def is_skytrain(row) -> bool:
    name = str(row.train_name)
    return "SkyTrain" in name


# get metro rail routes, in Vancouver that's the SkyTrain
def get_metro_rail() -> gpd.GeoDataFrame:
    railways: gpd.GeoDataFrame = read_from_cache("railways")
    railways["train_name"] = railways["name"]
    mask: gpd.GeoSeries = railways.apply(is_skytrain, axis=1)
    skytrain = railways[mask]
    return skytrain


def is_parking(row) -> bool:
    name = str(row.traffic_name)
    fclass = str(row.fclass)
    return "parking" in name.lower() or ("parking" in fclass and "under" not in fclass)


# get above ground parking lots
def get_parking() -> gpd.GeoDataFrame:
    traffic: gpd.GeoDataFrame = read_from_cache("traffic")
    traffic["traffic_name"] = traffic["name"]
    mask: gpd.GeoSeries = traffic.apply(is_parking, axis=1)
    parking = traffic[mask]
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


def get_roads() -> gpd.GeoDataFrame:
    raw_roads: gpd.GeoDataFrame = read_from_cache("roads")

    raw_graph: nx.Graph = gdf_to_graph(raw_roads)
    raw_graph.remove_edges_from(nx.selfloop_edges(raw_graph))

    graph = largest_component(raw_graph)
    crs = {"init": "epsg:4326"}
    roads = graph_to_gdf(graph).to_crs(crs=crs)
    return roads


# main function and entry point of program execution
if __name__ == "__main__":
    folder = argv[1]

    # if there is no cache of location-limmited files then create one
    if not cache_osm_exists():
        cache_from_osm(folder)

    roads = get_roads()
    graph = gdf_to_graph(roads)

    path_nodes: list[tuple[float, float]] = shortest_path(
        graph, Location(-122.924745, 49.279980), Location(-122.917446, 49.278985)
    )

    path_graph: nx.MultiGraph = graph.subgraph(path_nodes)

    landuse: gpd.GeoDataFrame = read_from_cache("landuse")

    roads_plot = roads.plot()
    path_gdf = graph_to_gdf(path_graph)
    path_polt = path_gdf.plot(ax=roads_plot, color="red")
    landuse.plot(ax=path_polt, color="green")
    plt.show()
    input()
