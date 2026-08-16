import networkx as nx
from fastapi import APIRouter, HTTPException, Request, status

from routeforger.api.response_models import RouteResponse
from routeforger.domain.scenario import Scenario
from routeforger.geo.geo_utilities import build_distance_graph
from routeforger.geo.geocoding import (
    AddressNotFoundError,
    AddressOutsideGraphError,
    GeocodingServiceError,
    map_addresses_to_graph,
)
from routeforger.geo.road_graph import build_real_route
from routeforger.optimization.search import (
    RouteNotFoundError,
    beam_search,
)
from routeforger.optimization.state import create_initial_state, get_relevant_nodes
from routeforger.output.serializer import serialize_route

router = APIRouter()


@router.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Report whether the API process is running."""
    return {"status": "ok"}


@router.post(
    "/routes",
    response_model=RouteResponse,
    tags=["routes"],
)
def create_route(scenario: Scenario, request: Request) -> RouteResponse:
    """Create an optimized delivery route for a scenario."""
    road_graph = request.app.state.road_graph
    district_polygon = request.app.state.district_polygon

    try:
        map_addresses_to_graph(scenario, road_graph, district_polygon)

        initial_state = create_initial_state(scenario)
        relevant_nodes = get_relevant_nodes(initial_state, scenario)
        distance_graph = build_distance_graph(relevant_nodes, road_graph)
        solution = beam_search(initial_state, scenario, distance_graph)
        route = build_real_route(solution, road_graph)

        return RouteResponse.model_validate(
            serialize_route(scenario, route, road_graph)
        )
    
    except AddressNotFoundError as error:
        # Return structured information so the UI can mark the exact field.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "address_not_found",
                "address": error.address,
                "message": str(error),
            },
        ) from error
    except AddressOutsideGraphError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "address_outside_graph",
                "address": error.address,
                "message": str(error),
            },
        ) from error
    except RouteNotFoundError as error:
        # All inputs are valid, but no stop order can satisfy the constraints.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error
    except GeocodingServiceError as error:
        # The address may be valid, but the external geocoder could not answer.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        ) from error
    except (nx.NetworkXNoPath, nx.NodeNotFound) as error:
        # Geocoded points can occasionally fall in disconnected portions of the
        # drivable graph, making a road route between them impossible.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The requested locations are not connected by the road network.",
        ) from error
