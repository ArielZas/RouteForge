import networkx as nx
import osmnx as ox
from shapely.geometry import MultiPolygon, Polygon

from routeforger.optimization.state import SearchState


def load_road_graph() -> tuple[nx.MultiDiGraph, Polygon | MultiPolygon]:
    """Load the drivable Tel Aviv District road graph."""
    district_polygon = ox.geocode_to_gdf(
        "Tel Aviv District, Israel"
    ).geometry.iloc[0]
    if not isinstance(district_polygon, (Polygon, MultiPolygon)):
        raise TypeError("Tel Aviv District boundary is not a polygon")

    road_graph = ox.graph.graph_from_polygon(
        district_polygon,
        network_type="drive",
    )

    road_graph = ox.routing.add_edge_speeds(road_graph)
    road_graph = ox.routing.add_edge_travel_times(road_graph)

    return road_graph, district_polygon


def build_real_route(
    solution: list[SearchState], 
    road_graph: nx.MultiDiGraph
) -> list[int]:
    """Convert optimized stops into road-graph paths."""
    if not solution:
        return []
    
    route = []
    for idx in range(len(solution)-1):
        src_node = solution[idx].current_node
        dst_node = solution[idx+1].current_node
        path_nodes = nx.shortest_path(
            road_graph,
            src_node,
            dst_node,
            weight="travel_time"
        )
        route += path_nodes
    return route
