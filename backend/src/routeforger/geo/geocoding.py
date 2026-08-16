import networkx as nx
import osmnx as ox
from osmnx._errors import InsufficientResponseError, ResponseStatusCodeError
from requests.exceptions import RequestException
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry

from routeforger.domain.scenario import Scenario


class AddressNotFoundError(ValueError):
    """Raised when the geocoding service cannot resolve an address."""

    def __init__(self, address: str) -> None:
        self.address = address
        super().__init__(f"address not found: {address}")


class AddressOutsideGraphError(ValueError):
    """Raised when a resolved address is outside the loaded road graph."""

    def __init__(self, address: str) -> None:
        self.address = address
        super().__init__(
            f"address is outside the loaded road graph: {address}"
        )


class GeocodingServiceError(RuntimeError):
    """Raised when the external geocoding service cannot complete a request."""


def address_to_node(
    address: str,
    road_graph: nx.MultiDiGraph,
    district_polygon: BaseGeometry,
) -> int:
    """Map an in-district address to its nearest road node."""
    try:
        latitude, longitude = ox.geocode(address)
    except InsufficientResponseError as error:
        raise AddressNotFoundError(address) from error
    except (RequestException, ResponseStatusCodeError) as error:
        raise GeocodingServiceError(
            "the geocoding service is temporarily unavailable"
        ) from error

    if not district_polygon.covers(Point(longitude, latitude)):
        raise AddressOutsideGraphError(address)

    return ox.distance.nearest_nodes(road_graph, X=longitude, Y=latitude)


def map_addresses_to_graph(
    scenario: Scenario,
    road_graph: nx.MultiDiGraph,
    district_polygon: BaseGeometry,
) -> None:
    """Map every scenario address onto the road graph."""
    for courier in scenario.couriers:
        courier.start_node = address_to_node(
            courier.start_address,
            road_graph,
            district_polygon,
        )

    for package in scenario.packages:
        package.source_node = address_to_node(
            package.source_address,
            road_graph,
            district_polygon,
        )

        package.destination_node = address_to_node(
            package.destination_address,
            road_graph,
            district_polygon,
        )
