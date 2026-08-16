import json
import networkx as nx
from pathlib import Path
from typing import Any

from routeforger.domain.scenario import Scenario

def serialize_route(
    scenario: Scenario, 
    route: list[int],
    road_graph: nx.MultiDiGraph,

) -> dict[str, Any]:
    """Convert a route into frontend-friendly data."""
    nodes = road_graph.nodes
    current_time = scenario.couriers[0].start_time
    total_distance = 0.0
    arrival_times: list[float] = []

    if route:
        arrival_times.append(current_time)
        for source, destination in zip(route, route[1:]):
            if source == destination:
                arrival_times.append(current_time)
                continue
            edges = road_graph[source][destination].values()
            edge = min(edges, key=lambda data: data.get("travel_time", float("inf")))
            current_time += edge.get("travel_time", 0.0)
            total_distance += edge.get("length", 0.0)
            arrival_times.append(current_time)

    packages = {package.id: package for package in scenario.packages}
    picked_up: set[int] = set()
    delivered_at: dict[int, float] = {}
    stops: list[dict[str, Any]] = []
    for index, node in enumerate(route):
        events: list[dict[str, Any]] = []
        for package in scenario.packages:
            if package.source_node == node and package.id not in picked_up:
                picked_up.add(package.id)
                events.append({"type": "pickup", "package_id": package.id})
        for package in scenario.packages:
            if (
                package.destination_node == node
                and package.id in picked_up
                and package.id not in delivered_at
            ):
                delivered_at[package.id] = arrival_times[index]
                events.append({"type": "delivery", "package_id": package.id})
        if events:
            stops.append({
                "node": node,
                "latitude": nodes[node]["y"],
                "longitude": nodes[node]["x"],
                "arrival_time": arrival_times[index],
                "events": events,
            })

    serialized_packages = []
    for package_id, package in packages.items():
        data = package.model_dump()
        delivery_time = delivered_at.get(package_id)
        data["delivery_time"] = delivery_time
        data["deadline_met"] = (
            delivery_time is not None and delivery_time <= package.deadline
        )
        serialized_packages.append(data)

    return {
        "courier": scenario.couriers[0].model_dump(),
        "packages": serialized_packages,
        "stops": stops,
        "total_distance": total_distance,
        "total_duration": current_time - scenario.couriers[0].start_time,
        "route": [
            {
                "node": node,
                "latitude": nodes[node]["y"],
                "longitude": nodes[node]["x"],
                "arrival_time": arrival_times[index],
            }
            for index, node in enumerate(route)
        ],
    }


def save_json(output: dict[str, Any], destination: str | Path) -> None:
    """Save serialized route data as JSON."""
    with Path(destination).open("w", encoding="utf-8") as destination_file:
        json.dump(output, destination_file, ensure_ascii=False, indent=2)
