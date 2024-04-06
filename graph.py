import networkx as nx
from collections import namedtuple
from util import *
from math import sqrt
from typing import Callable, List

"""
Collected networkx graph utility functions
"""


# Latitude and longitude coords of a point
Location = namedtuple("Location", ["latitude", "longitude"])


# Get single largest connected component of graph
def largest_component(graph: nx.MultiGraph) -> nx.MultiGraph:
    # Find all connected components and sort by size
    connected_components: list[nx.MultiGraph] = nx.connected_components(graph)
    sorted_componets: list[nx.MultiGraph] = sorted(
        connected_components, key=len, reverse=True
    )
    # Return largest connected component as a subgraph
    largest_component: nx.MultiGraph = sorted_componets[0]
    return graph.subgraph(largest_component)


# Get the nearest node to a point in a graph
def nearest_node(graph: nx.Graph, pos: Location) -> tuple[float, float] | None:
    nodes: list[tuple[float, float]] = list(graph.nodes())
    nearest: tuple[float, float] | None = None
    min_distance_square: float = float("inf")
    for node in nodes:
        dy: float = node[0] - pos[0]
        dx: float = node[1] - pos[1]
        distance_square: float = (dy) ** 2 + (dx) ** 2
        if distance_square < min_distance_square:
            min_distance_square = distance_square
            nearest = node
    return nearest


# Get the shortest path between two points in a graph
def shortest_path(
    graph: nx.multigraph.Graph,
    start: Location,
    end: Location,
    weight_function: Callable[[tuple[float, float], tuple[float, float]], float],
) -> list[tuple[float, float]]:
    # Compute the nearest nodes to the start and end points
    start_node: tuple[float, float] = nearest_node(graph, start)
    end_node: tuple[float, float] = nearest_node(graph, end)

    if start_node == end_node:
        # If the start and end nodes are the same, there is no path between
        # Let the user off with a warning
        warning(f"Path nodes are identical. {start_node}")
        return []

    # Compute distance weights to the search graph
    search_graph: nx.Graph = nx.Graph()
    graph_maxspeed = nx.get_edge_attributes(graph, "maxspeed")
    graph_fclass = nx.get_edge_attributes(graph, "fclass")
    for edge in graph.edges(keys=True):
        u: tuple[float, float] = edge[0]
        v: tuple[float, float] = edge[1]
        maxspeed: float = graph_maxspeed[edge]
        fclass: str = graph_fclass[edge]
        weight = weight_function(u, v, maxspeed=maxspeed, fclass=fclass)
        search_graph.add_edge(u, v, weight=weight)

    # Throw an exception if the dijkstra path finding fails
    try:
        path: list[tuple[float, float]] = nx.dijkstra_path(
            search_graph, start_node, end_node, weight="weight"
        )
        return path
    except:
        message: str = (
            f"Cannot find a path between {start} and {end}. Search nodes are {start_node} and {end_node}"
        )
        raise Exception(message)
