import networkx as nx

from dataclasses import dataclass, field
from routeforger.domain.scenario import Scenario
from routeforger.time_utils import seconds_to_time_string


@dataclass(frozen=True)
class SearchState():
    current_node: int
    current_time: int
    picked_up: frozenset[int]
    delivered: frozenset[int]
    late_packages: frozenset[int]
    # the distance the courier made to reach this state
    travel_cost_so_far: float = field(compare=False, hash=False)

    @property
    def current_time_display(self) -> str:
        """Format the state's time for display."""
        return seconds_to_time_string(self.current_time % 86_400)


def create_initial_state(scenario: Scenario) -> SearchState:
    """Create the courier's starting search state."""
    # since there is only 1 courier in V1
    courier = scenario.couriers[0]

    if courier.start_node is None:
        raise ValueError("courier must be geocoded before creating the initial state")

    picked_up = {
        package.id
        for package in scenario.packages
        if package.source_node == courier.start_node
    }

    return SearchState(
        current_node=courier.start_node,
        current_time=courier.start_time,
        picked_up=frozenset(picked_up),
        delivered=frozenset(),
        late_packages=frozenset(), 
        travel_cost_so_far=0,
    )


def get_relevant_nodes(state: SearchState, scenario: Scenario) -> list[int]:
    """List nodes still relevant to unfinished deliveries."""
    nodes = [state.current_node]

    for package in scenario.packages:
        if package.id in state.delivered:
            continue
        if package.destination_node is not None:
            nodes.append(package.destination_node)
        if package.id not in state.picked_up and package.source_node is not None:
            nodes.append(package.source_node)

    return nodes


def get_next_stop_nodes(state: SearchState, scenario: Scenario) -> set[int]:
    """List valid stops for the next state expansion."""
    nodes: set[int] = set()

    for package in scenario.packages:
        if package.id in state.delivered:
            continue

        if package.id in state.picked_up:
            if package.destination_node is not None:
                nodes.add(package.destination_node)
        elif package.source_node is not None:
            nodes.add(package.source_node)

    nodes.discard(state.current_node)
    return nodes


def expand_state(
    state: SearchState, 
    scenario: Scenario,
    distance_graph: nx.DiGraph
) -> list[SearchState]:
    """Generate states reachable from the current node."""
    states = []
    current_node = state.current_node

    for neighbor in get_next_stop_nodes(state, scenario):
        if not distance_graph.has_edge(current_node, neighbor):
            continue

        travel_duration = distance_graph[current_node][neighbor][
            "duration_seconds"
        ]
        current_time = state.current_time + round(travel_duration)

        picked_up = set(state.picked_up)
        delivered = set(state.delivered)
        late_packages = set(state.late_packages)

        # check if there are any packages to pick
        picked_up |= {
            package.id
            for package in scenario.packages
            if package.source_node == neighbor
        }

        # check if any are late
        late_packages |= {
            package.id
            for package in scenario.packages
            if current_time > package.deadline and 
            package.id not in state.delivered
        }

        # check if there are packages to deliver
        delivered |= {
            package.id
            for package in scenario.packages
            if package.destination_node == neighbor and
            package.id in picked_up
        }

        next_state = SearchState(
            current_node=neighbor,
            current_time=current_time,
            picked_up=frozenset(picked_up),
            delivered=frozenset(delivered),
            late_packages=frozenset(late_packages),
            travel_cost_so_far=state.travel_cost_so_far + travel_duration,
        )
        states.append(next_state)
    return states


def is_goal_state(state: SearchState, scenario: Scenario) -> bool:
    """Check whether every package is delivered."""
    return len(state.delivered) == len(scenario.packages)
