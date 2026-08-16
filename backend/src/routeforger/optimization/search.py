import heapq
from itertools import count

import networkx as nx

from routeforger.optimization.state import SearchState, expand_state, is_goal_state
from routeforger.domain.scenario import Scenario
from routeforger.optimization.heuristic import f_score


class SearchLimitExceededError(RuntimeError):
    """Raised when the algorithm exceeds its expansion limit."""


class RouteNotFoundError(RuntimeError):
    """Raised when no valid delivery route exists."""


def reconstruct_path(
    goal_state: SearchState,
    came_from: dict[SearchState, SearchState | None],
) -> list[SearchState]:
    """Rebuild the state path ending at the goal."""
    state_list = [goal_state]
    current_state = came_from[state_list[-1]]
    while current_state is not None:
        state_list.append(current_state)
        current_state = came_from[state_list[-1]]
    state_list.reverse()
    return state_list


def frontier_priority(
    state: SearchState,
    scenario: Scenario,
    distance_graph: nx.DiGraph,
) -> tuple[float, int, int]:
    """Calculate a state's ordered frontier priority."""
    return (
        f_score(state, scenario, distance_graph),
        len(state.late_packages),
        -len(state.delivered),
    )


def beam_search(
    init_state: SearchState,
    scenario: Scenario,
    distance_graph: nx.DiGraph,
) -> list[SearchState]:
    """Find a delivery route with beam search."""
    beam_width = 100
    beam = [init_state]
    best_cost: dict[SearchState, float] = {
        init_state: init_state.travel_cost_so_far,
    }
    came_from: dict[SearchState, SearchState | None] = {init_state: None}

    while beam:
        candidates: list[tuple[tuple[float, int, int], SearchState]] = []

        for current_state in beam:
            if is_goal_state(current_state, scenario):
                return reconstruct_path(current_state, came_from)

            for neighbor in expand_state(current_state, scenario, distance_graph):
                known_cost = best_cost.get(neighbor)
                if (
                    known_cost is not None
                    and neighbor.travel_cost_so_far >= known_cost
                ):
                    continue

                best_cost[neighbor] = neighbor.travel_cost_so_far
                came_from[neighbor] = current_state
                candidates.append(
                    (frontier_priority(neighbor, scenario, distance_graph), neighbor)
                )

        beam = [
            state
            for _, state in heapq.nsmallest(
                beam_width, candidates, key=lambda candidate: candidate[0]
            )
        ]

    raise RouteNotFoundError("no valid delivery route found")


def astar(
    init_state: SearchState,
    scenario: Scenario,
    distance_graph: nx.DiGraph,
    max_expansions: int = 50_000,
) -> list[SearchState]:
    """Find a delivery route with A* search."""
    counter = count()
    frontier: list[tuple[float, int, int, int, SearchState]] = []
    initial_priority = frontier_priority(init_state, scenario, distance_graph)
    heapq.heappush(frontier, (*initial_priority, next(counter), init_state))
    best_cost: dict[SearchState, float] = {
        init_state: init_state.travel_cost_so_far,
    }
    came_from: dict[SearchState, SearchState | None] = {
        init_state: None,
    }
    expansions = 0

    while frontier:
        if expansions >= max_expansions:
            raise SearchLimitExceededError(
                f"A* search exceeded {max_expansions} expansions"
            )

        *_, current_state = heapq.heappop(frontier)

        if current_state.travel_cost_so_far > best_cost[current_state]:
            continue

        if is_goal_state(current_state, scenario):
            return reconstruct_path(current_state, came_from)
        
        neighbor_states = expand_state(current_state, scenario, distance_graph)

        for neighbor in neighbor_states:
            # pruning
            known_cost = best_cost.get(neighbor)
            if (
                known_cost is not None
                and neighbor.travel_cost_so_far >= known_cost
            ):
                continue

            best_cost[neighbor] = neighbor.travel_cost_so_far
            came_from[neighbor] = current_state
            priority = frontier_priority(
                neighbor, scenario, distance_graph,
            )
            heapq.heappush(frontier, (*priority, next(counter), neighbor))

        expansions += 1

    raise RouteNotFoundError("no valid delivery route found")
