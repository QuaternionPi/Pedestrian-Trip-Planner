import momepy as mpy
import networkx as nx
import geopandas as gpd
from shapely.geometry import LineString


# Adapted from https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
# Terminal Codes for style
class TerminalStyle:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Print a message in color
def print_color(message: any, color_code: str) -> None:
    print(f"{color_code}{message}{TerminalStyle.DEFAULT}")


# Print a blue [INFO] message to inform the user of something
def info(message: any) -> None:
    print_color(f"[INFO] {message}", TerminalStyle.OKBLUE)


# Print a yellow [WARN] message to warn the user of something
def warning(message: any) -> None:
    print_color(f"[WARN] {message}", TerminalStyle.WARNING)


# Turn a GeoPandas.GeoDataFrame to a networkx.MultiGraph of edges
def gdf_to_graph(gdf: gpd.GeoDataFrame) -> nx.MultiGraph:
    return mpy.gdf_to_nx(gdf, approach="primal").to_undirected()


# Turn a networkx.MultiGraph to a GeoPandas.GeoDataFrame
def graph_to_gdf(graph: nx.MultiGraph) -> gpd.GeoDataFrame:
    return mpy.nx_to_gdf(graph)[1]


# Turn a shapely.LineString to a series of separate shapely.LineStrings
def segment(linestring: LineString) -> map:
    return map(LineString, zip(linestring.coords, linestring.coords[1:]))


# Split the edges of a GeoPandas.GeoDataFrame into individual LineStrings that span 2 points
def split_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gpd.GeoDataFrame(columns=["geometry"])
    edges = gdf.apply(lambda row: segment(row.geometry), axis=1)
    i = 0
    for edge in edges:
        for linestring in edge:
            # Add line-by-line
            result.loc[i] = linestring
            i += 1

    return result
