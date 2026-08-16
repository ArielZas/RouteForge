from routeforger.api.response_models import RouteResponse


def test_route_response_accepts_serialized_route_shape() -> None:
    """The documented API model matches the serializer's response structure."""
    response = RouteResponse.model_validate(
        {
            "courier": {
                "id": 1,
                "start_address": "Start",
                "start_node": 10,
                "start_time": 21_600,
            },
            "packages": [
                {
                    "id": 1,
                    "source_address": "Pickup",
                    "source_node": 20,
                    "destination_address": "Delivery",
                    "destination_node": 30,
                    "deadline": 32_400,
                    "delivery_time": 22_000.0,
                    "deadline_met": True,
                }
            ],
            "stops": [
                {
                    "node": 20,
                    "latitude": 32.1,
                    "longitude": 34.8,
                    "arrival_time": 21_800.0,
                    "events": [{"type": "pickup", "package_id": 1}],
                }
            ],
            "total_distance": 1_000.0,
            "total_duration": 400.0,
            "route": [
                {
                    "node": 10,
                    "latitude": 32.0,
                    "longitude": 34.8,
                    "arrival_time": 21_600.0,
                }
            ],
        }
    )

    assert response.packages[0].deadline_met is True
    assert response.stops[0].events[0].type == "pickup"
