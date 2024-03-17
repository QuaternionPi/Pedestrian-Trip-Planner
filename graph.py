import networkx as nx
from collections import namedtuple
from util import *
from math import sqrt

Location = namedtuple("Location", ["latitude", "longitude"])


# get single largest connected component of graph
def largest_component(graph: nx.Graph) -> nx.Graph:
    componets = sorted(nx.connected_components(graph), key=len, reverse=True)
    largest_component = componets[0]
    return graph.subgraph(largest_component)


# get the nearest node to a point in a graph
def nearest_node(graph: nx.Graph, pos: Location) -> tuple[float, float] | None:
    nodes: list[tuple[float, float]] = list(graph.nodes())
    nearest: tuple[float, float] | None = None
    min_distance_square: float = float("inf")
    for node in nodes:
        dy = node[0] - pos[0]
        dx = node[1] - pos[1]
        distance_square = (dy) ** 2 + (dx) ** 2
        if distance_square < min_distance_square:
            min_distance_square = distance_square
            nearest = node
    return nearest


# get the shortest path between two points in a graph
def shortest_path(
    graph: nx.multigraph.Graph,
    start: Location,
    end: Location,
    weight: str = "length",
) -> list[tuple[float, float]]:
    start_node = nearest_node(graph, start)
    end_node = nearest_node(graph, end)

    search_graph = nx.Graph()
    search_graph.add_edges_from(graph)
    for u, v in graph.edges():
        dy = u[0] - v[0]
        dx = u[1] - v[1]
        distance = sqrt(dx**2 + dy**2)
        search_graph.add_edge(u, v, length=distance)

    if start_node == end_node:
        warning(f"Path nodes are identical. {start_node}")
        return []
    try:
        path = nx.dijkstra_path(search_graph, start_node, end_node, weight=weight)
        return path
    except:
        message: str = (
            f"Cannot find a path between {start} and {end}. Search nodes are {start_node} and {end_node}"
        )
        raise Exception(message)
