import sys
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
from shapely.geometry import Point


# useful for graphing
# https://gis.stackexchange.com/questions/239633/how-to-convert-a-shapefile-into-a-graph-in-which-use-dijkstra
# https://medium.com/analytics-vidhya/interative-map-with-osm-directions-and-networkx-582c4f3435bc


pd.options.display.max_rows = 5000  # Max rows pandas will print in a DataFrame


# Function to check if a point is within the specified geographic bounds
def is_within_bounds(
    pos: tuple[float, float],
    xmin: float = -123.3,
    xmax: float = -122.5,
    ymin: float = 49.0,
    ymax: float = 49.4,
) -> bool:
    # Default is the longitude and latitude bounds for the lower mainland
    lon, lat = pos
    return xmin <= lon <= xmax and ymin <= lat <= ymax


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


# Define a dictionary mapping land use types to niceness scores
land_use_niceness_scores = {
    # Positive impact
    'nature_reserve': 0,
    'park': 0,
    'retail': 0,
    'forest': 0,
    'recreation_ground': 0,
    'grass': 0,
    'commercial': 0,
    'meadow': 0,
    'orchard': 0,
    'vineyard': 0,

    # Neutral impact
    'residential': 5,
    'health': 5,
    'scrub': 10,
    'cemetary': 10,

    # Negative impact
    'industrial': 15,
    'railway': 15,
    'farmland': 15,
    'allotments': 15,
    'quarry': 20,
    'highway': 20,
    'construction': 20,
    'military': 20,

    # May need to scale the scores for balanced route optimization
}


def point_niceness(pos: tuple[float, float]) -> float:
    """
    Computes the niceness of a position based on surrounding land use.

    Parameters:
    - pos: The (longitude, latitude) tuple for the location.

    Returns:
    - The niceness score for the position.
    """
    point = Point(pos)

    # May need to adjust buffer radius in degrees
    # 0.0001 degrees ≈ 10 m in Vancouver
    buffer_radius = 0.0003

    search_area = point.buffer(buffer_radius)

    # Filter landuse GeoDataFrame for features within the search area
    # Directly use the global landuse variable
    intersecting_landuse = landuse[landuse.intersects(search_area)]

    # Initialize the niceness score
    niceness_score = 0

    # Calculate the niceness score based on intersecting land use types
    for _, landuse_row in intersecting_landuse.iterrows():
        landuse_type = landuse_row['fclass']
        # Update the niceness score based on the land use type's predefined score
        # Default score is 2 for unspecified land use types
        niceness_score += land_use_niceness_scores.get(landuse_type, 2)

    return niceness_score


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
    # Shortest path on weighted edges
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
    # Check if the user has provided the minimum required argument (the path to OSM data)
    if len(sys.argv) < 2:
        info("You need to provide the path to the OSM data as an argument to run the project.")
        info()
        info("Correct formats for running the project are:")
        info("1) Default mode (using predefined locations for start and end points):")
        info("   python3 main.py <path-to-osm-unzipped>")
        info("   Example: python3 main.py ./british-columbia-latest-free.shp")
        info()
        info("2) Custom mode (specifying start and end points):")
        info("   python3 main.py <path-to-osm-unzipped> <start_lon> <start_lat> <end_lon> <end_lat>")
        info("   Example: python3 main.py ./british-columbia-latest-free.shp -123.1423 49.2871 -123.1217 49.2744")
        info()
        info("Please replace <path-to-osm-unzipped> with the actual path to your OSM data,")
        info("and <start_lon>, <start_lat>, <end_lon>, <end_lat> with your desired coordinates.")
        sys.exit(1)

    # Extract the path to OSM data from command-line arguments
    path_to_osm: str = sys.argv[1]

    # If there is no cache of location-limited files then create one
    if not cache_osm_exists():
        cache_from_osm(path_to_osm)

    # Global declaration of the landuse GeoDataFrame
    global landuse
    # Load landuse data for route analysis in `point_niceness` function
    landuse: gpd.GeoDataFrame = read_from_cache("landuse")

    roads: gpd.GeoDataFrame = get_walkable_roads()
    graph: nx.MultiGraph = gdf_to_graph(roads)

    # Default coordinates for English Bay and YaleTown Roundhouse
    default_start: Location = Location(-123.1423, 49.2871)  # English Bay
    default_end: Location = Location(-123.1217, 49.2744)  # YaleTown Roundhouse

    # Some other points for testing the code:
    # Canada Place: -123.1111, 49.2888
    # Rogers Arena: -123.1091, 49.2778
    # Metropolis at Metrotown: -123.0000, 49.2273
    # Simon Fraser University: -122.9202, 49.2791

    # Initialize start and end points with default values
    start: Location = default_start
    end: Location = default_end

     # Check user provided custom start and end points
    if len(sys.argv) == 6:
        try:
            # Attempt to parse the custom coordinates
            start = (float(sys.argv[2]), float(sys.argv[3]))
            end = (float(sys.argv[4]), float(sys.argv[5]))

            # Validate the provided coordinates
            if not is_within_bounds(start) or not is_within_bounds(end):
                warning("Provided points are out of bounds. Using default locations.")
                start, end = default_start, default_end

        except ValueError:
            warning("Invalid coordinates format. Using default locations.")
            start, end = default_start, default_end

    info(f"Using start point: {start} and end point: {end}")

    # Path from start to end
    path_graph: nx.MultiGraph = plan_route_graph(graph, start, end)
    save_paths_as_gpx([plan_route(graph, start, end)])

    # Plot path and roads, with roads in the background
    roads_plot: tuple[plt.Figure, plt.Axes] = roads.plot()

    path_gdf: nx.MultiGraph = graph_to_gdf(path_graph)
    path_plot: tuple[plt.Figure, plt.Axes] = path_gdf.plot(ax=roads_plot, color="red")

    # Plot landuse over top of roads and the path
    landuse.plot(ax=path_plot, color="green")
    plt.show()
