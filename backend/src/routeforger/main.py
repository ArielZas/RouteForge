from pathlib import Path

from routeforger.geo.geo_utilities import build_distance_graph
from routeforger.geo.geocoding import map_addresses_to_graph
from routeforger.geo.road_graph import build_real_route, load_road_graph
from routeforger.input.json_loader import load_scenario
from routeforger.optimization.search import beam_search
from routeforger.optimization.state import create_initial_state, get_relevant_nodes
from routeforger.output.serializer import save_json, serialize_route


def main() -> None:
    """Run the complete route-planning workflow."""
    # 1. Load + validate the input
    scenario = load_scenario(Path("data/scenario.json"))
    print("finished step 1 of loading + validation of input....")

    # 2. Prepare geographic data
    road_graph, district_polygon = load_road_graph()
    map_addresses_to_graph(
        scenario,
        road_graph,
        district_polygon,
    )
    print("finished step 2 of preparing geo data....")

    # 3. Build initial search state
    initial_state = create_initial_state(scenario)
    relevant_nodes = get_relevant_nodes(initial_state, scenario)
    distance_graph = build_distance_graph(relevant_nodes, road_graph)
    print("finished step 3 of setting init state...")

    # 4. Run the route search
    solution = beam_search(
        initial_state,
        scenario,
        distance_graph
    )
    print("finished step 4 of running the search algorithm...")

    # 5. Convert the sequence of stops into actual road paths
    route = build_real_route(
        solution,
        road_graph
    )
    print("finished step 5 of coverting the solution into road nodes...")

    # 6. Serialize result into frontend-friendly format
    output = serialize_route(
        scenario,
        route,
        road_graph,
    )
    print("finished step 6 of serializing the solution...")

    # 7. Save/output it for the frontend
    save_json(output, "route_result.json")
    print("finished step 7 of outputing the solution via json...")


if __name__ == "__main__":
    main()
