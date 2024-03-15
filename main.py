from sys import argv
import os
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import momepy
from collections import namedtuple
import util


pd.options.display.max_rows = 5000

# useful for graphing
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra
# https://medium.com/analytics-vidhya/interative-map-with-osm-directions-and-networkx-582c4f3435bc

Location = namedtuple("Location", ["latitude", "longitude"])


def largest_component(graph: nx.Graph) -> nx.Graph:
    componets = sorted(nx.connected_components(graph), key=len, reverse=True)
    largest_component = componets[0]
    return graph.subgraph(largest_component)


def within_zone(input: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    # the latitude and longitude bounds for the lower mainland
    """
    xmin = -123.3
    xmax = -122.5
    ymin = 49.0
    ymax = 49.4
    """
    # test bounds to run faster
    xmin = -123.0
    xmax = -122.3
    ymin = 49.0
    ymax = 49.3
    return input.cx[xmin:xmax, ymin:ymax]


def cache_zone(folder: str) -> None:
    if os.path.exists(folder) == False:
        raise Exception(f'"{folder}" does not exist')
    if os.path.isdir(folder) == False:
        raise Exception(f'"{folder} is not a folder')

    if os.path.exists("cache") == False:
        os.mkdir("cache")
    filenames: list[str] = [
        "gis_osm_landuse_a_free_1.shp",
        "gis_osm_railways_free_1.shp",
        "gis_osm_roads_free_1.shp",
        "gis_osm_traffic_a_free_1.shp",
    ]

    path_to_source = lambda filename: os.path.join(folder, filename)
    path_to_destination = lambda filename: os.path.join("cache", filename)

    for filename in filenames:
        source = path_to_source(filename)

        input_df: gpd.GeoDataFrame = gpd.read_file(source)
        output_df: gpd.GeoDataFrame = within_zone(input_df)

        destionation = path_to_destination(filename)
        output_df.to_file(destionation)


def rate_point(x: float, y: float):
    pass


def is_skytrain(row) -> bool:
    name = str(row.train_name)
    return "SkyTrain" in name


# get metro rail routes, in Vancouver that's the SkyTrain
def get_metro_rail() -> gpd.GeoDataFrame:
    railways: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_railways_free_1.shp")
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
    traffic: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_traffic_a_free_1.shp")
    traffic["traffic_name"] = traffic["name"]
    mask: gpd.GeoSeries = traffic.apply(is_parking, axis=1)
    parking = traffic[mask]
    return parking


def get_landuse_positive() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_landuse_a_free_1.shp")
    key: str = (
        "nature_reserve|park|retail|forest|recreation_ground|grass|commercial|meadow|orchard|vineyard"
    )
    positive: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return positive


def get_landuse_neutral() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_landuse_a_free_1.shp")
    key: str = "cemetary|scrub|health"
    neutral: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return neutral


def get_landuse_negative() -> gpd.GeoDataFrame:
    landuse: gpd.GeoDataFrame = gpd.read_file(f"cache/gis_osm_landuse_a_free_1.shp")
    key: str = "farmland|military|allotments|quarry"
    negative: gpd.GeoDataFrame = landuse[landuse["fclass"].str.contains(key)]
    return negative


def nearest_node(graph: nx.Graph, pos: Location) -> tuple[float, float] | None:
    nodes: list[tuple[float, float]] = list(graph.nodes())
    nearest: tuple[float, float] | None = None
    min_distance_square: float = float("inf")
    for node in nodes:
        distance_square = (node[0] - pos[0]) ** 2 + (node[1] - pos[1]) ** 2
        if distance_square < min_distance_square:
            min_distance_square = distance_square
            nearest = node
    return nearest


def shortest_path(
    graph: nx.multigraph.MultiGraph,
    start: Location,
    end: Location,
    weight: str = "length",
) -> list[tuple[float, float]]:
    start_node = nearest_node(graph, start)
    end_node = nearest_node(graph, end)
    if start_node == end_node:
        util.warning(f"path nodes are identical. {start_node}")
        return []
    try:
        path = nx.dijkstra_path(graph, start_node, end_node, weight=weight)
        return path
    except:
        message: str = (
            f"Cannot find a path between {start} and {end}. Search nodes are {start_node} and {end_node}"
        )
        raise Exception(message)


def get_roads() -> gpd.GeoDataFrame:
    raw_roads: gpd.GeoDataFrame = gpd.read_file("cache/gis_osm_roads_free_1.shp")

    raw_graph: nx.multigraph.Graph = momepy.gdf_to_nx(
        raw_roads,
        approach="primal",
    )
    raw_graph.remove_edges_from(nx.selfloop_edges(raw_graph))

    graph = largest_component(raw_graph)
    roads = graph_to_gdf(graph)
    return roads


def gdf_to_graph(gdf: gpd.GeoDataFrame) -> nx.MultiGraph:
    return momepy.gdf_to_nx(gdf, approach="primal")


def graph_to_gdf(graph: nx.MultiGraph):
    return momepy.nx_to_gdf(graph)[1]


# main function and entry point of program execution
if __name__ == "__main__":
    folder = argv[1]

    # if there is no cache of location-limmited files then create one
    if (os.path.exists("cache") == False) or (len(os.listdir("cache")) != 4 * 5):
        if os.path.exists("cache"):
            for filename in os.listdir("cache"):
                os.remove(f"cache/{filename}")
            os.rmdir("cache")
        cache_zone(folder)

    roads = get_roads()
    graph = gdf_to_graph(roads)

    path_nodes: list[tuple[float, float]] = shortest_path(
        graph, Location(-123.0, 49.05), Location(-122.2, 49.25)
    )

    path_graph: nx.MultiGraph = graph.subgraph(path_nodes)

    roads_plot = roads.plot()
    path_gdf = graph_to_gdf(path_graph)
    path_gdf.plot(ax=roads_plot, color="red")
    plt.show()
