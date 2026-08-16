import networkx as nx
import osmnx as ox


def build_distance_graph(
        mapped_locations: list[int],
        road_graph: nx.MultiDiGraph, 
) -> nx.DiGraph:
    """Build pairwise travel distances between mapped locations."""
    
    distance_graph = nx.DiGraph()
    distance_graph.add_nodes_from(mapped_locations)    

    for loc1 in mapped_locations:
        for loc2 in mapped_locations:
            if loc1 == loc2:
                continue
            path = nx.shortest_path(
                road_graph,
                loc1,
                loc2,
                weight="travel_time",
            )

            distance_graph.add_edge(
                loc1,
                loc2,
                duration_seconds = nx.path_weight(
                    road_graph, path, weight="travel_time"
                ),
                distance_meters = nx.path_weight(
                    road_graph, path, weight="length"
                ),            
            )
            

    return distance_graph


def mst(
    mapped_locations: list[int],
    distance_graph: nx.DiGraph,
) -> nx.Graph:
    """Build a minimum spanning tree for the mapped locations."""

    undirected_graph = nx.Graph()
    undirected_graph.add_nodes_from(mapped_locations)

    for index, node_a in enumerate(mapped_locations):
        for node_b in mapped_locations[index + 1:]:
            forward_duration = distance_graph.get_edge_data(
                node_a, node_b, {}
            ).get("duration_seconds", float("inf"))
            backward_duration = distance_graph.get_edge_data(
                node_b, node_a, {}
            ).get("duration_seconds", float("inf"))

            undirected_graph.add_edge(
                node_a,
                node_b,
                duration_seconds=min(forward_duration, backward_duration),
            )

    return nx.minimum_spanning_tree(
        undirected_graph,
        weight="duration_seconds",
    )
