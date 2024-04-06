from sys import argv
import os
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from collections import namedtuple
from typing import Callable, List
from util import *
from cache_from_osm import cache_from_osm, cache_osm_exists, read_from_cache
from graph import *
from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint
from datetime import datetime

pd.options.display.max_rows = 5000  # Max rows pandas will print in a dataframe

# useful for graphing
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra
# https://medium.com/analytics-vidhya/interative-map-with-osm-directions-and-networkx-582c4f3435bc


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
    walkable_classes = [
        "footway",
        "pedestrian",
        "path",
        "residential",
        "living_street",
        "unclassified",
        "service",
        "track",
        "tertiary",
    ]

    # Create a boolean mask that identifies rows where the 'fclass' column matches any of the walkable classes
    walkable_criteria = roads["fclass"].isin(walkable_classes)

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


# Simple function to compute niceness based on surounding landuse
def point_niceness(pos: tuple[float, float]) -> float:

    # TODO: How nice is position, defined by landuse

    return 0


# Simple function to compute niceness based on the road
def road_niceness(
    u: tuple[float, float],
    v: tuple[float, float],
    maxspeed: int | None,
    fclass: str | None,
) -> float:
    result = 0
    if maxspeed is int:
        result += max(maxspeed - 30, 0)
    if fclass is str and fclass not in [
        "pedestrian",
        "living_street",
        "unclassified",
        "track",
        "path",
        "bridleway",
        "cycleway",
        "footway",
        "steps",
    ]:
        result += 40

    return result


# Function weights the value of an edge
def niceness(
    u: tuple[float, float],
    v: tuple[float, float],
    maxspeed: float | None,
    fclass: str | None,
) -> float:
    return length(u, v) * (
        road_niceness(u, v, maxspeed=maxspeed, fclass=fclass)
        + point_niceness(u)
        + point_niceness(v)
    )


# Length of an edge
def length(u: tuple[float, float], v: tuple[float, float]) -> float:
    dy: float = u[0] - v[0]
    dx: float = u[1] - v[1]
    distance: float = sqrt(dx**2 + dy**2)
    return distance


def plan_route(
    roads_graph: nx.MultiGraph, start: Location, end: Location
) -> list[tuple[float, float]]:
    # Shortest path on weigthed edges
    path_nodes: list[tuple[float, float]] = shortest_path(
        roads_graph, start, end, niceness
    )
    return path_nodes


# Same as plan route, but returns a graph
def plan_route_graph(
    roads_graph: nx.MultiGraph, start: Location, end: Location
) -> nx.MultiGraph:
    path_nodes: list[tuple[float, float]] = plan_route(roads_graph, start, end)
    path_graph: nx.MultiGraph = roads_graph.subgraph(path_nodes)

    return path_graph


def save_paths_as_gpx(
    paths: list[list[tuple[float, float]]],
    directory: str = "./",
    file_prefix: str = "path",
) -> None:
    """
    Converts a list of NetworkX MultiGraph objects into GPX format and saves the data locally.

    :param paths: A list of NetworkX MultiGraph objects, each representing a path.
    :param directory: The directory to save the GPX files. Defaults to the current directory.
    :param file_prefix: Prefix for the GPX file names. Defaults to "path".

    Example usage: save_paths_as_gpx(paths, directory="path_to_directory", file_prefix="my_walk")
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    for path_number, path in enumerate(paths):
        gpx = GPX()

        # Create a GPX track for this path
        gpx_track = GPXTrack()
        gpx.tracks.append(gpx_track)

        # Create a segment in our GPX track
        gpx_segment = GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Iterate through each node in the MultiGraph to create track points
        for node in path:
            lat, lon = (node[1], node[0])
            gpx_segment.points.append(GPXTrackPoint(lat, lon))

        # Serialize the GPX object to a string
        gpx_data = gpx.to_xml()

        # Define the file path
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{file_prefix}_{path_number}_{timestamp}.gpx"
        file_path = os.path.join(directory, file_name)

        # Write the GPX string to a file
        with open(file_path, "w") as gpx_file:
            gpx_file.write(gpx_data)

        info(f"Saved GPX data to {file_path}")


# Main function and entry point of program execution
if __name__ == "__main__":
    folder: str = argv[1]

    # If there is no cache of location-limited files then create one
    if not cache_osm_exists():
        cache_from_osm(folder)

    english_bay: Location = Location(-123.1423, 49.2871)
    yaletown_roundhouse: Location = Location(-123.1217, 49.2744)

    roads: gpd.GeoDataFrame = get_walkable_roads()
    graph: nx.MultiGraph = gdf_to_graph(roads)

    # Path from start to end
    start: Location = english_bay
    end: Location = yaletown_roundhouse
    path_graph: nx.MultiGraph = plan_route_graph(graph, start, end)
    save_paths_as_gpx([plan_route(graph, start, end)])

    # Plot path and roads, with roads in the background
    roads_plot: tuple[plt.Figure, plt.Axes] = roads.plot()

    path_gdf: nx.MultiGraph = graph_to_gdf(path_graph)
    path_polt: tuple[plt.Figure, plt.Axes] = path_gdf.plot(ax=roads_plot, color="red")

    # Plot landuse over top of roads and the path
    landuse: gpd.GeoDataFrame = read_from_cache("landuse")
    landuse.plot(ax=path_polt, color="green")
    plt.show()
    input()
