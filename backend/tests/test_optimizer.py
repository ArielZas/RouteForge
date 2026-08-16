import networkx as nx
import pytest

from routeforger.domain.courier import Courier
from routeforger.domain.package import Package
from routeforger.domain.scenario import Scenario
from routeforger.optimization.search import (
    RouteNotFoundError,
    SearchLimitExceededError,
    astar,
    beam_search,
    frontier_priority,
)
from routeforger.optimization.state import (
    SearchState,
    create_initial_state,
    expand_state,
    get_next_stop_nodes,
    get_relevant_nodes,
)


def make_scenario() -> Scenario:
    """Create a small geocoded scenario for optimizer tests."""
    scenario = Scenario(
        couriers=[Courier(id=1, start_address="Start", start_time=0)],
        packages=[
            Package(
                id=1,
                source_address="Pickup",
                destination_address="Delivery",
                deadline=100,
            )
        ],
    )
    scenario.couriers[0].start_node = 1
    scenario.packages[0].source_node = 1
    scenario.packages[0].destination_node = 2
    return scenario


def make_distance_graph() -> nx.DiGraph:
    """Create a minimal directed travel-time graph."""
    graph = nx.DiGraph()
    graph.add_edge(1, 2, duration_seconds=10)
    graph.add_edge(2, 1, duration_seconds=10)
    return graph


def test_initial_state_picks_up_packages_at_start() -> None:
    """Verify packages at the start node are picked up immediately."""
    state = create_initial_state(make_scenario())

    assert state.picked_up == frozenset({1})


def test_expansion_only_visits_relevant_nodes() -> None:
    """Verify expansion ignores nodes unrelated to unfinished deliveries."""
    scenario = make_scenario()
    state = create_initial_state(scenario)
    graph = make_distance_graph()
    graph.add_edge(1, 99, duration_seconds=1)

    neighbors = expand_state(state, scenario, graph)

    assert [neighbor.current_node for neighbor in neighbors] == [2]


def test_unpicked_destination_is_only_used_by_heuristic() -> None:
    """Verify an unpicked destination is estimated but not expanded."""
    scenario = make_scenario()
    scenario.packages[0].source_node = 2
    scenario.packages[0].destination_node = 3
    state = create_initial_state(scenario)

    assert set(get_relevant_nodes(state, scenario)) == {1, 2, 3}
    assert get_next_stop_nodes(state, scenario) == {2}


def test_delivered_package_does_not_become_late() -> None:
    """Verify completed packages remain on time as time advances."""
    scenario = make_scenario()
    state = SearchState(
        current_node=1,
        current_time=200,
        picked_up=frozenset({1}),
        delivered=frozenset({1}),
        late_packages=frozenset(),
        travel_cost_so_far=0,
    )

    assert expand_state(state, scenario, make_distance_graph()) == []
    assert state.late_packages == frozenset()


def test_priority_uses_late_packages_as_a_tiebreaker() -> None:
    """Verify lateness breaks ties between equal cost estimates."""
    scenario = make_scenario()
    graph = make_distance_graph()
    on_time = create_initial_state(scenario)
    late = SearchState(
        current_node=on_time.current_node,
        current_time=on_time.current_time,
        picked_up=on_time.picked_up,
        delivered=on_time.delivered,
        late_packages=frozenset({1}),
        travel_cost_so_far=on_time.travel_cost_so_far,
    )

    assert frontier_priority(on_time, scenario, graph) < frontier_priority(
        late, scenario, graph
    )


def test_astar_raises_when_expansion_limit_is_reached() -> None:
    """Verify exhausting the A* search budget has a distinct error."""
    scenario = make_scenario()

    with pytest.raises(SearchLimitExceededError):
        astar(
            create_initial_state(scenario),
            scenario,
            make_distance_graph(),
            max_expansions=0,
        )


def test_astar_raises_when_route_does_not_exist() -> None:
    """Verify an exhausted frontier reports an unavailable route."""
    scenario = make_scenario()
    graph = nx.DiGraph()
    graph.add_node(1)

    with pytest.raises(RouteNotFoundError):
        astar(create_initial_state(scenario), scenario, graph)


def test_astar_delivers_package() -> None:
    """Verify A* returns a path that delivers every package."""
    scenario = make_scenario()

    path = astar(
        create_initial_state(scenario),
        scenario,
        make_distance_graph(),
    )

    assert path[-1].delivered == frozenset({1})
    assert path[-1].late_packages == frozenset()


def test_beam_search_delivers_package() -> None:
    """Verify beam search returns a complete delivery path."""
    scenario = make_scenario()

    path = beam_search(
        create_initial_state(scenario),
        scenario,
        make_distance_graph(),
    )

    assert path[-1].delivered == frozenset({1})
    assert path[-1].late_packages == frozenset()
