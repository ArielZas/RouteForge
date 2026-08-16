from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResponseModel(BaseModel):
    """Base configuration shared by all API response models."""

    model_config = ConfigDict(extra="forbid")


class CourierResponse(ResponseModel):
    """Courier information returned with a calculated route."""

    id: int = Field(gt=0)
    start_address: str
    start_node: int
    start_time: int = Field(ge=0, lt=86_400)


class PackageResponse(ResponseModel):
    """Package details and the result of its delivery attempt."""

    id: int = Field(gt=0)
    source_address: str
    source_node: int
    destination_address: str
    destination_node: int
    deadline: int = Field(ge=0, lt=86_400)
    delivery_time: float | None
    deadline_met: bool


class StopEventResponse(ResponseModel):
    """A pickup or delivery performed at a route stop."""

    type: Literal["pickup", "delivery"]
    package_id: int = Field(gt=0)


class RoutePointResponse(ResponseModel):
    """One road-network coordinate in the rendered route."""

    node: int
    latitude: float
    longitude: float
    arrival_time: float


class StopResponse(RoutePointResponse):
    """A route point at which one or more package events occur."""

    events: list[StopEventResponse]


class RouteResponse(ResponseModel):
    """Complete result returned by the route-optimization endpoint."""

    courier: CourierResponse
    packages: list[PackageResponse]
    stops: list[StopResponse]
    total_distance: float = Field(ge=0)
    total_duration: float = Field(ge=0)
    route: list[RoutePointResponse]
