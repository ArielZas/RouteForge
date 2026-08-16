from types import SimpleNamespace

import pytest
from fastapi import HTTPException, status

from routeforger.api.routes import create_route
from routeforger.domain.courier import Courier
from routeforger.domain.package import Package
from routeforger.domain.scenario import Scenario
from routeforger.geo.geocoding import AddressNotFoundError, GeocodingServiceError


def make_scenario() -> Scenario:
    """Create a minimal valid request scenario for router error tests."""
    return Scenario(
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


def make_request() -> SimpleNamespace:
    """Create the application-state portion of a request used by the router."""
    return SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(road_graph=object(), district_polygon=object())
        )
    )


def test_unknown_address_returns_structured_field_information(monkeypatch) -> None:
    """The UI receives enough information to identify the invalid input."""
    def raise_address_error(*_args) -> None:
        raise AddressNotFoundError("Unknown Place")

    monkeypatch.setattr(
        "routeforger.api.routes.map_addresses_to_graph",
        raise_address_error,
    )

    with pytest.raises(HTTPException) as caught:
        create_route(make_scenario(), make_request())

    assert caught.value.status_code == status.HTTP_400_BAD_REQUEST
    assert caught.value.detail == {
        "code": "address_not_found",
        "address": "Unknown Place",
        "message": "address not found: Unknown Place",
    }


def test_geocoding_service_failure_returns_503(monkeypatch) -> None:
    """The API identifies an unavailable geocoder as a temporary failure."""
    def raise_service_error(*_args) -> None:
        raise GeocodingServiceError(
            "the geocoding service is temporarily unavailable"
        )

    monkeypatch.setattr(
        "routeforger.api.routes.map_addresses_to_graph",
        raise_service_error,
    )

    with pytest.raises(HTTPException) as caught:
        create_route(make_scenario(), make_request())

    assert caught.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "temporarily unavailable" in caught.value.detail
