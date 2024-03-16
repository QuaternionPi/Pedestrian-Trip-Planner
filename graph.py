import networkx as nx
from collections import namedtuple
from util import *

Location = namedtuple("Location", ["latitude", "longitude"])


# get single largest connected component of graph
def largest_component(graph: nx.Graph) -> nx.Graph:
    componets = sorted(nx.connected_components(graph), key=len, reverse=True)
    largest_component = componets[0]
    return graph.subgraph(largest_component)


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
        warning(f"Path nodes are identical. {start_node}")
        return []
    try:
        path = nx.dijkstra_path(graph, start_node, end_node, weight=weight)
        return path
    except:
        message: str = (
            f"Cannot find a path between {start} and {end}. Search nodes are {start_node} and {end_node}"
        )
        raise Exception(message)
