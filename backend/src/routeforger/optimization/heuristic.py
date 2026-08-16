import networkx as nx

from routeforger.domain.scenario import Scenario
from routeforger.geo.geo_utilities import mst
from routeforger.optimization.state import SearchState, get_relevant_nodes


def f_score(
    state: SearchState,
    scenario: Scenario,
    distance_graph: nx.DiGraph,
) -> float:
    """Combine traveled and estimated remaining costs."""
    return state.travel_cost_so_far + estimate_remaining_cost(
        state,
        scenario,
        distance_graph,
    )


def estimate_remaining_cost(
    state: SearchState,
    scenario: Scenario,
    distance_graph: nx.DiGraph,
) -> float:
    """Estimate remaining travel with a spanning tree."""
    mapped_locations = get_relevant_nodes(state, scenario)
    mst_graph = mst(mapped_locations, distance_graph)
    return mst_graph.size(weight="duration_seconds")
