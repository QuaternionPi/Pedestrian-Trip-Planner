import momepy as mpy
import networkx as nx
import geopandas as gpd
from shapely.geometry import LineString


# adapted from https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class TerminalText:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    DEFAULT = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_color(message: any, color_code: str) -> None:
    print(f"{color_code}{message}{TerminalText.DEFAULT}")


def info(message: any) -> None:
    print_color(f"[INFO] {message}", TerminalText.OKBLUE)


def warning(message: any) -> None:
    print_color(f"[WARN] {message}", TerminalText.WARNING)


def gdf_to_graph(gdf: gpd.GeoDataFrame) -> nx.Graph:
    return mpy.gdf_to_nx(gdf, approach="primal").to_undirected()


def graph_to_gdf(graph: nx.MultiGraph):
    return mpy.nx_to_gdf(graph)[1]


def segment(linestring: LineString) -> map:
    return map(LineString, zip(linestring.coords, linestring.coords[1:]))


def split_geometry(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    result = gpd.GeoDataFrame(columns=["geometry"])
    edges = gdf.apply(lambda row: segment(row.geometry), axis=1)
    i = 0
    for edge in edges:
        for linestring in edge:
            result.loc[i] = linestring
            i += 1

    return result
