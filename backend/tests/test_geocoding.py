from unittest.mock import Mock

import networkx as nx
import pytest
from osmnx._errors import InsufficientResponseError, ResponseStatusCodeError

from routeforger.geo.geocoding import (
    AddressNotFoundError,
    GeocodingServiceError,
    address_to_node,
)


def test_missing_address_has_a_user_correctable_error(monkeypatch) -> None:
    """A valid geocoder response with no result means the address is unknown."""
    monkeypatch.setattr(
        "routeforger.geo.geocoding.ox.geocode",
        Mock(side_effect=InsufficientResponseError("no result")),
    )

    with pytest.raises(AddressNotFoundError, match="Unknown Place"):
        address_to_node("Unknown Place", nx.MultiDiGraph(), Mock())


def test_geocoder_http_failure_has_a_service_error(monkeypatch) -> None:
    """An upstream HTTP failure is different from an unknown address."""
    monkeypatch.setattr(
        "routeforger.geo.geocoding.ox.geocode",
        Mock(side_effect=ResponseStatusCodeError("rate limited")),
    )

    with pytest.raises(GeocodingServiceError, match="temporarily unavailable"):
        address_to_node("Azrieli Center", nx.MultiDiGraph(), Mock())
